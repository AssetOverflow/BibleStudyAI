from typing import List, Dict, Any
import hashlib
from loguru import logger

from database.milvus_vector import MilvusManager
from database.neo4j_graph import Neo4jManager
from database.redis_cache import get_redis_manager
from data_ingestion.embedder import Embedder
from services.ai_integration import ai_integration_client, ModelProvider
from prompts.graph_prompt import ENTITY_EXTRACTION_PROMPT
from utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import json


class SearchTools:
    """
    A collection of tools for searching the knowledge graph and vector database.
    """

    def __init__(self):
        logger.info("Initializing SearchTools...")
        # Initialize components with error handling
        try:
            self.milvus_manager = MilvusManager()
            logger.info("Milvus manager initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Milvus manager: {e}")
            self.milvus_manager = None

        try:
            self.neo4j_manager = Neo4jManager()
            logger.info("Neo4j manager initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Neo4j manager: {e}")
            self.neo4j_manager = None

        self.embedder = Embedder()
        self.redis_manager = get_redis_manager()
        self.collection_name = "bible_verses"
        logger.info("SearchTools initialized.")

    async def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search in Milvus with caching and improved scoring.

        Args:
            query (str): The search query.
            top_k (int): The number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of search results with enhanced metadata.
        """
        logger.info(f"Performing vector search for query: '{query}'")

        # Check if Milvus is available
        if self.milvus_manager is None or not self.milvus_manager.is_available():
            logger.warning("Milvus manager not available, returning empty results")
            return []

        # Create cache key
        query_hash = hashlib.sha256(
            f"vector_search:{query}:{top_k}".encode()
        ).hexdigest()

        # Check cache first
        cached_results = await self.redis_manager.get_cached_search_results(query_hash)
        if cached_results:
            logger.debug(f"Using cached vector search results for query: '{query}'")
            return cached_results

        try:
            query_embedding = await self.embedder.embed_text(query)
            if not query_embedding:
                logger.warning("Could not generate embedding for the query.")
                return []

            results = self.milvus_manager.search(
                collection_name=self.collection_name,
                query_vectors=[query_embedding],
                top_k=top_k,
            )

            # Process results with enhanced scoring and metadata
            processed_results = []
            if results:
                for hit in results[0]:  # Results is a list of lists of hits
                    entity = hit.entity

                    # Enhanced scoring: normalize distance to similarity score
                    similarity_score = (
                        1.0 / (1.0 + hit.distance) if hit.distance > 0 else 1.0
                    )

                    result = {
                        "id": entity.get("id"),
                        "distance": hit.distance,
                        "similarity_score": similarity_score,
                        "text": entity.get("text"),
                        "metadata": {
                            "translation": entity.get("translation"),
                            "book": entity.get("book"),
                            "chapter": entity.get("chapter"),
                            "chunk_index": entity.get("chunk_index"),
                        },
                        "relevance_indicators": {
                            "text_length": len(entity.get("text", "")),
                            "has_keywords": self._check_query_keywords_in_text(
                                query, entity.get("text", "")
                            ),
                        },
                    }
                    processed_results.append(result)

            # Sort by similarity score (highest first)
            processed_results.sort(key=lambda x: x["similarity_score"], reverse=True)

            # Cache the results
            await self.redis_manager.cache_search_results(query_hash, processed_results)

            return processed_results
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during vector search: {e}"
            )
            return []

    def _check_query_keywords_in_text(self, query: str, text: str) -> bool:
        """
        Checks if any keywords from the query appear in the text.
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        return len(query_words.intersection(text_words)) > 0

    async def _extract_entities_from_text(self, text: str) -> List[str]:
        """
        Uses an LLM to extract key entities from a text.
        """
        logger.info(f"Extracting entities from text: '{text[:100]}...'")
        if not text:
            return []

        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
        try:
            response_text = await ai_integration_client.generate_text(
                prompt=prompt,
                provider=ModelProvider.OPENAI,  # Or make this configurable
                system_prompt="You are a helpful assistant that only returns valid, well-formed JSON.",
            )
            cleaned_response = (
                response_text.strip().replace("```json", "").replace("```", "").strip()
            )
            data = json.loads(cleaned_response)
            entities = data.get("entities", [])
            logger.info(f"Extracted entities: {entities}")
            return entities
        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON for entity extraction. Response was:\n{response_text}"
            )
            return []
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during entity extraction: {e}"
            )
            return []

    def graph_search(
        self, entities: List[str], max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Performs an optimized search in the Neo4j knowledge graph with depth control.

        Args:
            entities (List[str]): A list of entity names to search for.
            max_depth (int): Maximum relationship depth to traverse.

        Returns:
            List[Dict[str, Any]]: A list of paths or subgraphs found.
        """
        if not entities:
            return []

        # Check if Neo4j is available
        if self.neo4j_manager is None:
            logger.warning("Neo4j manager not available, returning empty results")
            return []

        logger.info(
            f"Performing graph search for entities: {entities} with max depth: {max_depth}"
        )

        # Create cache key
        entities_key = "|".join(sorted(entities))
        cache_key = f"graph_search:{hashlib.sha256(entities_key.encode()).hexdigest()}:{max_depth}"

        try:
            # Check cache first (synchronous for graph search)
            # Note: We'd need async version of Neo4j operations for full async caching

            # Optimized query with depth control and relevance scoring
            cypher_query = f"""
            UNWIND $entities AS entityName
            MATCH (n)
            WHERE n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower(entityName)
            
            // Find related entities within specified depth
            OPTIONAL MATCH path = (n)-[*1..{max_depth}]-(m)
            WHERE m.name IS NOT NULL
            
            // Calculate relevance based on relationship distance and entity importance
            WITH n, m, path, 
                 CASE WHEN path IS NULL THEN 0 ELSE length(path) END as distance,
                 CASE WHEN n.importance IS NOT NULL THEN n.importance ELSE 1 END as n_importance,
                 CASE WHEN m.importance IS NOT NULL THEN m.importance ELSE 1 END as m_importance
            
            // Return results ordered by relevance
            RETURN DISTINCT n, m, 
                   relationships(path) as rels,
                   distance,
                   (n_importance + m_importance) / (distance + 1) as relevance_score
            ORDER BY relevance_score DESC
            LIMIT 100
            """

            results = self.neo4j_manager.query(
                cypher_query, {"entities": entities, "max_depth": max_depth}
            )

            # Process and enhance results
            processed_results = []
            for record in results:
                processed_result = {
                    "source_node": record.get("n", {}),
                    "target_node": record.get("m", {}),
                    "relationships": record.get("rels", []),
                    "distance": record.get("distance", 0),
                    "relevance_score": record.get("relevance_score", 0),
                    "relationship_types": (
                        [rel.type for rel in record.get("rels", [])]
                        if record.get("rels")
                        else []
                    ),
                }
                processed_results.append(processed_result)

            return processed_results

        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during graph search: {e}"
            )
            return []

    async def hybrid_search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Combines vector and graph search with intelligent result fusion and caching.

        Args:
            query (str): The search query.
            top_k (int): The number of top results for the vector search part.

        Returns:
            Dict[str, Any]: Enhanced results with fusion scoring and metadata.
        """
        logger.info(f"Performing hybrid search for query: '{query}'")

        # Create comprehensive cache key
        query_hash = hashlib.sha256(
            f"hybrid_search:{query}:{top_k}".encode()
        ).hexdigest()

        # Check cache first
        cached_results = await self.redis_manager.get_cached_search_results(query_hash)
        if cached_results:
            logger.debug(f"Using cached hybrid search results for query: '{query}'")
            return cached_results

        # 1. Vector Search with enhanced metadata
        vector_results = await self.vector_search(query, top_k=top_k)

        if not vector_results:
            empty_result = {
                "vector_results": [],
                "graph_results": [],
                "fusion_score": 0.0,
            }
            await self.redis_manager.cache_search_results(query_hash, empty_result)
            return empty_result

        # 2. Extract entities from the top vector search results (not just the first one)
        all_extracted_entities = set()
        for result in vector_results[
            : min(3, len(vector_results))
        ]:  # Use top 3 results
            text = result.get("text", "")
            entities = await self._extract_entities_from_text(text)
            all_extracted_entities.update(entities)

        extracted_entities = list(all_extracted_entities)

        # 3. Perform enhanced graph search
        graph_results = []
        if extracted_entities:
            graph_results = self.graph_search(extracted_entities, max_depth=2)
        else:
            # Fallback to using query terms
            logger.info("No entities extracted, using query terms for graph search.")
            query_terms = [
                term.strip() for term in query.split() if len(term.strip()) > 2
            ]
            graph_results = self.graph_search(query_terms, max_depth=1)

        # 4. Calculate fusion scores
        fusion_score = self._calculate_fusion_score(
            vector_results, graph_results, query
        )

        # 5. Prepare enhanced result structure
        enhanced_results = {
            "vector_results": vector_results,
            "graph_results": graph_results,
            "fusion_score": fusion_score,
            "extracted_entities": extracted_entities,
            "query_analysis": {
                "query_length": len(query),
                "query_terms": query.split(),
                "estimated_complexity": self._estimate_query_complexity(query),
            },
            "result_statistics": {
                "total_vector_results": len(vector_results),
                "total_graph_results": len(graph_results),
                "unique_entities_found": len(extracted_entities),
                "average_vector_similarity": (
                    sum(r.get("similarity_score", 0) for r in vector_results)
                    / len(vector_results)
                    if vector_results
                    else 0
                ),
            },
        }

        # Cache the enhanced results
        await self.redis_manager.cache_search_results(query_hash, enhanced_results)

        return enhanced_results

    def _calculate_fusion_score(
        self, vector_results: List[Dict], graph_results: List[Dict], query: str
    ) -> float:
        """
        Calculates a fusion score based on the quality and relevance of both search results.
        """
        if not vector_results and not graph_results:
            return 0.0

        # Vector component (30% weight)
        vector_score = 0.0
        if vector_results:
            avg_similarity = sum(
                r.get("similarity_score", 0) for r in vector_results
            ) / len(vector_results)
            keyword_bonus = sum(
                1
                for r in vector_results
                if r.get("relevance_indicators", {}).get("has_keywords", False)
            ) / len(vector_results)
            vector_score = (avg_similarity * 0.7 + keyword_bonus * 0.3) * 0.3

        # Graph component (70% weight) - knowledge graphs are often more precise
        graph_score = 0.0
        if graph_results:
            avg_relevance = sum(
                r.get("relevance_score", 0) for r in graph_results
            ) / len(graph_results)
            relationship_diversity = len(
                set(
                    rel_type
                    for r in graph_results
                    for rel_type in r.get("relationship_types", [])
                )
            )
            graph_score = (
                avg_relevance * 0.8 + min(relationship_diversity / 10, 1.0) * 0.2
            ) * 0.7

        return min(vector_score + graph_score, 1.0)

    def _estimate_query_complexity(self, query: str) -> str:
        """
        Estimates the complexity of a query based on length and structure.
        """
        word_count = len(query.split())
        if word_count <= 3:
            return "simple"
        elif word_count <= 7:
            return "medium"
        else:
            return "complex"

    def close_connections(self):
        """Closes database connections and Redis connection."""
        if self.neo4j_manager:
            self.neo4j_manager.close()
        # Note: Redis connection will be closed when the manager is garbage collected
        # or explicitly closed elsewhere
        logger.info("SearchTools connections closed.")


# Example Usage
async def main():
    tools = SearchTools()
    try:
        query = "light and darkness"

        print("--- Vector Search Results ---")
        vector_res = await tools.vector_search(query)
        print(vector_res)

        print("\n--- Graph Search Results ---")
        graph_res = tools.graph_search("God")
        print(graph_res)

        print("\n--- Hybrid Search Results ---")
        hybrid_res = await tools.hybrid_search(query)
        print(hybrid_res)

    finally:
        tools.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
