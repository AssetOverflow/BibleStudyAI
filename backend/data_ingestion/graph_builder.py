import json
from typing import Dict, Any
from loguru import logger

from services.ai_integration import ai_integration_client, ModelProvider
from prompts.graph_prompt import GRAPH_GENERATION_PROMPT


class GraphBuilder:
    """
    Uses an LLM to extract entities and relationships from text to build a knowledge graph.
    """

    def __init__(
        self, provider: ModelProvider = ModelProvider.OPENAI, model: str = "gpt-4o"
    ):
        """
        Initializes the GraphBuilder.

        Args:
            provider (ModelProvider): The AI provider to use for graph generation.
            model (str): The specific model to use.
        """
        self.provider = provider
        self.model = model
        logger.info(
            f"GraphBuilder initialized with provider: {provider.value}, model: {model}"
        )

    async def build_graph_from_text(self, text: str) -> Dict[str, Any]:
        """
        Generates a graph structure (nodes and edges) from a given text chunk.

        Args:
            text (str): The text chunk to process.

        Returns:
            Dict[str, Any]: A dictionary containing "nodes" and "edges" as parsed from the LLM response.
                           Returns an empty dict if parsing fails.
        """
        if not text:
            return {"nodes": [], "edges": []}

        prompt = GRAPH_GENERATION_PROMPT.format(text=text)

        try:
            response_text = await ai_integration_client.generate_text(
                prompt=prompt,
                provider=self.provider,
                model=self.model,
                system_prompt="You are a helpful assistant that only returns valid, well-formed JSON.",
            )

            # Clean the response to ensure it's valid JSON
            # LLMs sometimes wrap their JSON output in markdown code blocks
            cleaned_response = (
                response_text.strip().replace("```json", "").replace("```", "").strip()
            )

            graph_data = json.loads(cleaned_response)

            # Basic validation of the returned structure
            if "nodes" not in graph_data or "edges" not in graph_data:
                logger.warning("LLM response did not contain 'nodes' or 'edges' keys.")
                return {"nodes": [], "edges": []}

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


# Example usage:
if __name__ == "__main__":
    import asyncio

    async def main():
        graph_builder = GraphBuilder()
        sample_text = "And God said, Let there be light: and there was light. And God saw the light, that it was good: and God divided the light from the darkness."
        graph = await graph_builder.build_graph_from_text(sample_text)
        print(json.dumps(graph, indent=2))

    asyncio.run(main())
