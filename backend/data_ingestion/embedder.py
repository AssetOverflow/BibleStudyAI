from typing import List
from loguru import logger

from services.ai_integration import ai_integration_client, ModelProvider


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

    async def embed_text(self, text: str) -> List[float]:
        """
        Generates an embedding for a single text chunk with caching.

        Args:
            text (str): The text chunk to embed.

        Returns:
            List[float]: The embedding vector, or None if generation failed.
        """
        if not text:
            return None

        try:
            # Check cache first
            cache_key = f"embedding:{hash(text)}"
            cached_embedding = await self._get_cached_embedding(cache_key)
            if cached_embedding:
                logger.debug(f"Using cached embedding for text: {text[:50]}...")
                return cached_embedding

            # Generate new embedding
            embedding = await ai_integration_client.get_embedding(
                text=text, provider=self.provider, model=self.model
            )

            # Cache the result
            if embedding:
                await self._cache_embedding(cache_key, embedding)

            return embedding
        except Exception as e:
            logger.opt(exception=True).error(f"Failed to generate embedding: {e}")
            return None

    async def _get_cached_embedding(self, cache_key: str) -> List[float]:
        """
        Retrieves cached embedding from Redis.
        """
        try:
            from database.redis_cache import RedisManager

            redis_manager = RedisManager()
            cached_data = await redis_manager.get(cache_key)
            if cached_data:
                import json

                return json.loads(cached_data)
        except Exception as e:
            logger.debug(f"Cache miss or error: {e}")
        return None

    async def _cache_embedding(
        self, cache_key: str, embedding: List[float], ttl: int = 86400
    ):
        """
        Caches embedding in Redis with TTL.
        """
        try:
            from database.redis_cache import RedisManager
            import json

            redis_manager = RedisManager()
            await redis_manager.set(cache_key, json.dumps(embedding), ttl)
        except Exception as e:
            logger.debug(f"Failed to cache embedding: {e}")


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
