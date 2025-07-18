from typing import List, Dict, Any
from loguru import logger

from ..database.milvus_vector import MilvusManager
from ..database.neo4j_graph import Neo4jManager
from .embedder import Embedder
from ..services.ai_integration import ai_integration_client, ModelProvider
from ..prompts.graph_prompt import ENTITY_EXTRACTION_PROMPT
from ..utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import json


class SearchTools:
    """
    A collection of tools for searching the knowledge graph and vector database.
    """

    def __init__(self):
        logger.info("Initializing SearchTools...")
        self.milvus_manager = MilvusManager()
        self.neo4j_manager = Neo4jManager(
            uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD
        )
        self.embedder = Embedder()
        self.collection_name = "bible_verses"
        logger.info("SearchTools initialized.")

    async def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search in Milvus.

        Args:
            query (str): The search query.
            top_k (int): The number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of search results.
        """
        logger.info(f"Performing vector search for query: '{query}'")
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

            # Process results to be more usable
            processed_results = []
            if results:
                for hit in results[0]:  # Results is a list of lists of hits
                    entity = hit.entity
                    processed_results.append(
                        {
                            "id": entity.get("id"),
                            "score": hit.distance,
                            "text": entity.get("text"),
                            "metadata": {
                                "translation": entity.get("translation"),
                                "book": entity.get("book"),
                                "chapter": entity.get("chapter"),
                            },
                        }
                    )
            return processed_results
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during vector search: {e}"
            )
            return []

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

    def graph_search(self, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Performs a search in the Neo4j knowledge graph for a list of entities, finding their relationships.

        Args:
            entities (List[str]): A list of entity names to search for.

        Returns:
            List[Dict[str, Any]]: A list of paths or subgraphs found.
        """
        if not entities:
            return []

        logger.info(f"Performing graph search for entities: {entities}")
        # This query finds nodes matching any of the provided entities and returns them
        # and any relationships they have with other nodes.
        cypher_query = """
        UNWIND $entities AS entityName
        MATCH (n)
        WHERE n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower(entityName)
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, r, m
        LIMIT 50
        """
        try:
            results = self.neo4j_manager.query(cypher_query, {"entities": entities})
            return results
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during graph search: {e}"
            )
            return []

    async def hybrid_search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Combines vector and graph search for a comprehensive result set.
        First, it performs a vector search to find relevant text, then uses the entities
        from that text to perform a targeted graph search.

        Args:
            query (str): The search query.
            top_k (int): The number of top results for the vector search part.

        Returns:
            Dict[str, Any]: A dictionary containing 'vector_results' and 'graph_results'.
        """
        logger.info(f"Performing hybrid search for query: '{query}'")

        # 1. Vector Search
        vector_results = await self.vector_search(query, top_k=top_k)

        if not vector_results:
            return {"vector_results": [], "graph_results": []}

        # 2. Extract entities from the top vector search result
        top_text_result = vector_results[0].get("text", "")
        extracted_entities = await self._extract_entities_from_text(top_text_result)

        # 3. Perform graph search using the extracted entities
        graph_results = []
        if extracted_entities:
            graph_results = self.graph_search(extracted_entities)
        else:
            # Fallback to using the original query if no entities are extracted
            logger.info(
                "No entities extracted, falling back to original query for graph search."
            )
            graph_results = self.graph_search([query])

        return {"vector_results": vector_results, "graph_results": graph_results}

    def close_connections(self):
        """Closes the Neo4j driver connection."""
        self.neo4j_manager.close()
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
