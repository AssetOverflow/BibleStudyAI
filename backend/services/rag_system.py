import asyncio
from loguru import logger
from typing import Dict, Any, List

from ..agents.tools import SearchTools
from .ai_integration import ai_integration_client, ModelProvider


class RAGSystem:
    """
    The core Retrieval-Augmented Generation (RAG) system.
    It orchestrates retrieval from multiple sources (vector DB, graph DB)
    and uses an LLM to synthesize an answer based on the retrieved context.
    """

    def __init__(
        self, provider: ModelProvider = ModelProvider.OPENAI, model: str = "gpt-4o"
    ):
        """
        Initializes the RAGSystem.
        """
        logger.info("Initializing RAG System...")
        self.search_tools = SearchTools()
        self.provider = provider
        self.model = model
        self.system_prompt = self._construct_system_prompt()
        logger.info(
            f"RAG System initialized with provider: {provider.value}, model: {model}"
        )

    def _construct_system_prompt(self) -> str:
        """
        Creates the system prompt for the generation model.
        """
        return """You are an advanced AI assistant specializing in biblical studies and theology.
Your purpose is to answer user questions based on the provided context from both vector and graph database searches.
The context may include direct scripture passages (from vector search) and structured entity relationships (from graph search).

Instructions:
1.  Synthesize information from both 'Vector Context' and 'Graph Context' to formulate a comprehensive answer.
2.  If the context contains direct scripture, cite the book, chapter, and verse.
3.  If the context contains relationships between entities (e.g., 'God CREATED light'), incorporate these facts into your explanation.
4.  If the context does not provide enough information to answer the question, state that you cannot answer based on the provided information. Do not use outside knowledge.
5.  Present the answer in a clear, well-structured, and insightful manner.
"""

    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Formats the retrieved context into a string for the LLM prompt.
        """
        formatted_str = ""

        if context.get("vector_results"):
            formatted_str += "--- Vector Context (Scripture Passages) ---\n"
            for res in context["vector_results"]:
                meta = res.get("metadata", {})
                formatted_str += f"Source: {meta.get('translation', 'N/A')} {meta.get('book', 'N/A')} {meta.get('chapter', 'N/A')}\n"
                formatted_str += f"Text: {res.get('text', '')}\n\n"

        if context.get("graph_results"):
            formatted_str += "--- Graph Context (Entities and Relationships) ---\n"
            # A simple representation of graph data. This could be made more sophisticated.
            nodes = set()
            edges = []
            for record in context["graph_results"]:
                if record.get("n") and "name" in record["n"]:
                    nodes.add(record["n"]["name"])
                if record.get("m") and "name" in record["m"]:
                    nodes.add(record["m"]["name"])
                if record.get("r"):
                    start_node = (
                        record["n"]["name"]
                        if record.get("n") and "name" in record["n"]
                        else "Unknown"
                    )
                    end_node = (
                        record["m"]["name"]
                        if record.get("m") and "name" in record["m"]
                        else "Unknown"
                    )
                    # The relation type in neo4j driver is not a string, so we get its type name
                    rel_type = type(record["r"]).__name__
                    edges.append(f"({start_node})-[{rel_type}]->({end_node})")

            formatted_str += f"Entities: {', '.join(list(nodes))}\n"
            formatted_str += f"Relationships: {'; '.join(edges)}\n\n"

        return formatted_str.strip()

    async def answer_question(self, query: str) -> Dict[str, Any]:
        """
        Answers a user's question using the full RAG pipeline.

        Args:
            query (str): The user's question.

        Returns:
            A dictionary containing the generated answer and the source context.
        """
        logger.info(f"Answering question: '{query}'")

        # 1. Retrieve context using hybrid search
        retrieved_context = await self.search_tools.hybrid_search(query)

        if not retrieved_context.get("vector_results") and not retrieved_context.get(
            "graph_results"
        ):
            logger.warning("No context found for the query.")
            return {
                "answer": "I could not find any relevant information to answer your question.",
                "context": {},
            }

        # 2. Format context for the prompt
        formatted_context = self._format_context_for_prompt(retrieved_context)

        # 3. Generate answer with LLM
        user_prompt = f"Based on the following context, please answer this question: {query}\n\n--- Context ---\n{formatted_context}"

        try:
            answer = await ai_integration_client.generate_text(
                prompt=user_prompt,
                provider=self.provider,
                model=self.model,
                system_prompt=self.system_prompt,
            )

            return {"answer": answer, "context": retrieved_context}
        except Exception as e:
            logger.opt(exception=True).error(
                f"An error occurred during answer generation: {e}"
            )
            return {
                "answer": "I encountered an error while trying to generate an answer.",
                "context": retrieved_context,
            }

    def close(self):
        """Closes underlying connections."""
        self.search_tools.close_connections()
        logger.info("RAG System connections closed.")


# Example Usage
async def main():
    rag_system = RAGSystem()
    try:
        # NOTE: This example assumes you have run the ingestion pipeline first!
        # `python -m backend.data_ingestion.ingest`
        question = "What did God create on the first day?"
        result = await rag_system.answer_question(question)

        print("--- Question ---")
        print(question)
        print("\n--- Answer ---")
        print(result["answer"])
        print("\n--- Source Context ---")
        import json

        print(
            json.dumps(result["context"], indent=2, default=str)
        )  # Use default=str for Neo4j objects

    finally:
        rag_system.close()


if __name__ == "__main__":
    # To run this example:
    # 1. Make sure your .env file is configured.
    # 2. Run the ingestion script first: `python3 -m backend.data_ingestion.ingest`
    # 3. Then run this script: `python3 -m backend.services.rag_system`
    asyncio.run(main())
