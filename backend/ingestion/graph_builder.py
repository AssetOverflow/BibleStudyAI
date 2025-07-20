"""
Bible knowledge graph builder for extracting biblical entities and relationships using agentic pipeline.
"""

import json
from typing import Dict, Any
from loguru import logger

from agents.base_agents import get_graph_llm_client
from prompts.graph_prompt import GRAPH_GENERATION_PROMPT
from database.neo4j_graph import Neo4jManager
from database.redis_cache import RedisManager, generate_cache_key
from ingestion.chunker import DocumentChunk


class GraphBuilder:
    async def add_document_to_graph(
        self,
        chunks: list,
        document_title: str,
        document_source: str,
        document_metadata: dict = None,
        batch_size: int = 10,
    ) -> dict:
        """
        Add Bible document chunks to the knowledge graph in batches.

        Args:
            chunks: List of DocumentChunk objects
            document_title: Title of the Bible document
            document_source: Source of the document
            document_metadata: Additional metadata
            batch_size: Number of chunks to process in each batch

        Returns:
            Processing results
        """
        if not chunks:
            return {"episodes_created": 0, "errors": []}

        logger.info(
            f"Adding {len(chunks)} Bible chunks to knowledge graph for document: {document_title}"
        )

        episodes_created = 0
        errors = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            for chunk in batch:
                try:
                    passage_reference = (
                        chunk.metadata.get("passage_reference")
                        if hasattr(chunk, "metadata")
                        else None
                    )
                    episode_content = self._prepare_episode_content(
                        chunk, document_title, document_metadata
                    )
                    graph = await self.build_graph_from_text(
                        episode_content,
                        passage_reference=passage_reference,
                        source_description=document_source,
                    )
                    episodes_created += 1
                    logger.info(
                        f"✓ Added Bible chunk {chunk.index} to knowledge graph ({episodes_created}/{len(chunks)})"
                    )
                except Exception as e:
                    error_msg = (
                        f"Failed to add Bible chunk {chunk.index} to graph: {str(e)}"
                    )
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

        result = {
            "episodes_created": episodes_created,
            "total_chunks": len(chunks),
            "errors": errors,
        }
        logger.info(
            f"Graph building complete: {episodes_created} Bible chunks added, {len(errors)} errors"
        )
        return result

    def _prepare_episode_content(
        self,
        chunk: DocumentChunk,
        document_title: str,
        document_metadata: dict = None,
    ) -> str:
        """
        Prepare episode content for Bible passages, truncating if needed.

        Args:
            chunk: DocumentChunk
            document_title: Title of the document
            document_metadata: Additional metadata

        Returns:
            Formatted episode content
        """
        max_content_length = 6000
        content = chunk.content
        if len(content) > max_content_length:
            truncated = content[:max_content_length]
            last_sentence_end = max(
                truncated.rfind(". "), truncated.rfind("! "), truncated.rfind("? ")
            )
            if last_sentence_end > max_content_length * 0.7:
                content = truncated[: last_sentence_end + 1] + " [TRUNCATED]"
            else:
                content = truncated + "... [TRUNCATED]"
            logger.warning(
                f"Truncated Bible chunk {chunk.index} from {len(chunk.content)} to {len(content)} chars"
            )
        if document_title and len(content) < max_content_length - 100:
            episode_content = f"[Doc: {document_title[:50]}]\n\n{content}"
        else:
            episode_content = content
        return episode_content

    """
    Uses an LLM to extract biblical entities and relationships from text to build a Bible knowledge graph.
    """

    def __init__(self):
        self.llm_client = get_graph_llm_client()
        self.neo4j_manager = Neo4jManager()
        self.redis_manager = RedisManager()

    async def build_graph_from_text(
        self,
        text: str,
        passage_reference: str = None,
        source_description: str = None,
    ) -> Dict[str, Any]:
        """
        Generates a graph structure (nodes and edges) from a given Bible passage or chunk.

        Args:
            text (str): The Bible passage or chunk to process.
            passage_reference (str): Optional passage reference (e.g., Genesis 1:1-6).
            source_description (str): Optional source description.

        Returns:
            Dict[str, Any]: A dictionary containing "nodes" and "edges" as parsed from the LLM response.
        """
        if not text:
            return {"nodes": [], "edges": []}

        cache_key = generate_cache_key("bible_graph_generation", text)
        try:
            cached_graph = await self.redis_manager.get(cache_key)
            if cached_graph:
                logger.info(f"Cache hit for graph generation with key: {cache_key}")
                graph_data = json.loads(cached_graph)
            else:
                logger.info(f"Cache miss for graph generation with key: {cache_key}")
                prompt = GRAPH_GENERATION_PROMPT.format(text=text)
                response_text = await self.llm_client.generate_text(
                    prompt=prompt,
                    system_prompt="You are a helpful assistant that only returns valid, well-formed JSON representing biblical entities, relationships, and concepts.",
                )
                cleaned_response = (
                    response_text.strip()
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )
                graph_data = json.loads(cleaned_response)
                await self.redis_manager.set(
                    cache_key, json.dumps(graph_data), ttl=3600 * 24
                )

            if "nodes" not in graph_data or "edges" not in graph_data:
                logger.warning("LLM response did not contain 'nodes' or 'edges' keys.")
                return {"nodes": [], "edges": []}

            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            for node in nodes:
                label = node.get("label")
                props = node.get("properties", {})
                props["passage_reference"] = passage_reference
                await self.neo4j_manager.create_node(label, props, temporal=True)
            for edge in edges:
                src = edge.get("source")
                tgt = edge.get("target")
                rel_type = edge.get("type") or "MENTIONED_WITH"
                rel_props = edge.get("properties", {})
                cypher = (
                    f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) "
                    f"CREATE (a)-[r:{rel_type}]->(b) SET r += $props RETURN r"
                )
                await self.neo4j_manager.execute_query(
                    cypher, {"src": src, "tgt": tgt, "props": rel_props}
                )
            return graph_data

        except json.JSONDecodeError:
            logger.error(
                f"Failed to decode JSON from LLM response. Response was:\n{response_text}"
            )
            return {"nodes": [], "edges": []}
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during graph generation: {e}"
            )
            return {"nodes": [], "edges": []}


# Example usage for Bible knowledge graph
if __name__ == "__main__":
    import asyncio

    async def main():
        from ingestion.chunker import ChunkingConfig, create_chunker

        config = ChunkingConfig(
            chunk_size=50, use_semantic_splitting=False, mode="bible"
        )
        chunker = create_chunker(config)
        graph_builder = GraphBuilder()
        passage_reference = "Genesis 1:1-6"
        verses = [
            (1, "In the beginning God created the heaven and the earth."),
            (
                2,
                "And the earth was without form, and void; and darkness was upon the face of the deep.",
            ),
            (3, "And the Spirit of God moved upon the face of the waters."),
            (4, "And God said, Let there be light: and there was light."),
            (
                5,
                "And God saw the light, that it was good: and God divided the light from the darkness.",
            ),
            (
                6,
                "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.",
            ),
        ]
        chunks = await chunker.chunk_document(
            content=" ".join([v[1] for v in verses]),
            translation="KJV",
            book="Genesis",
            chapter=1,
            verses=verses,
        )
        print(f"Created {len(chunks)} Bible chunks")
        result = await graph_builder.add_document_to_graph(
            chunks=chunks,
            document_title="Genesis 1:1-6",
            document_source="KJV",
            document_metadata={"book": "Genesis", "chapter": 1},
        )
        print(f"Graph building result: {result}")

    asyncio.run(main())
