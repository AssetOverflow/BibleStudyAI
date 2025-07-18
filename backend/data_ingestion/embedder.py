from typing import List
from loguru import logger

from ..services.ai_integration import ai_integration_client, ModelProvider


class Embedder:
    """
    A service class for generating text embeddings using a specified AI provider.
    """

    def __init__(
        self,
        provider: ModelProvider = ModelProvider.OPENAI,
        model: str = "text-embedding-3-small",
    ):
        """
        Initializes the Embedder.

        Args:
            provider (ModelProvider): The AI provider to use for embeddings.
            model (str): The specific embedding model to use.
        """
        self.provider = provider
        self.model = model
        logger.info(
            f"Embedder initialized with provider: {provider.value}, model: {model}"
        )

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text chunks.

        Args:
            texts (List[str]): A list of text chunks to embed.

        Returns:
            List[List[float]]: A list of embeddings, where each embedding is a list of floats.
        """
        if not texts:
            return []

        try:
            # The get_embedding method in AIIntegration is designed to handle a single string,
            # but the underlying OpenAI client can handle a list. We'll call it in a loop for now,
            # but this could be optimized to make a single batch call to the provider.
            embeddings = []
            for text in texts:
                embedding = await ai_integration_client.get_embedding(
                    text=text, provider=self.provider, model=self.model
                )
                if embedding:
                    embeddings.append(embedding)

            if len(embeddings) != len(texts):
                logger.warning(
                    "Number of generated embeddings does not match number of input texts."
                )

            return embeddings
        except Exception as e:
            logger.opt(exception=True).error(f"Failed to generate embeddings: {e}")
            return []


# Example usage:
if __name__ == "__main__":
    import asyncio

    async def main():
        embedder = Embedder()
        sample_texts = [
            "This is the first sentence.",
            "Here is another sentence for embedding.",
        ]
        embeddings = await embedder.get_embeddings(sample_texts)
        for text, embedding in zip(sample_texts, embeddings):
            print(f"--- TEXT ---")
            print(text)
            print(f"--- EMBEDDING (first 5 dims) ---")
            print(embedding[:5])
            print()

    asyncio.run(main())
