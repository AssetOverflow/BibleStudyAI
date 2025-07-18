import asyncio
import json
from typing import Any, Optional
import redis.asyncio as redis
from loguru import logger

from utils.config import settings


class RedisManager:
    """
    Manages Redis connections and operations for caching.
    """

    def __init__(self):
        self.redis_client = None
        self._connection_pool = None

    async def connect(self):
        """
        Establishes connection to Redis.
        """
        if self.redis_client is None:
            try:
                self._connection_pool = redis.ConnectionPool(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    max_connections=20,
                )
                self.redis_client = redis.Redis(connection_pool=self._connection_pool)

                # Test the connection
                await self.redis_client.ping()
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

    async def disconnect(self):
        """
        Closes Redis connection.
        """
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
        logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[str]:
        """
        Retrieves a value from Redis.

        Args:
            key (str): The cache key.

        Returns:
            Optional[str]: The cached value or None if not found.
        """
        if not self.redis_client:
            await self.connect()

        try:
            value = await self.redis_client.get(key)
            return value
        except Exception as e:
            logger.error(f"Error retrieving key {key} from Redis: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """
        Sets a value in Redis with TTL.

        Args:
            key (str): The cache key.
            value (str): The value to cache.
            ttl (int): Time to live in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            await self.connect()

        try:
            await self.redis_client.set(key, value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Deletes a key from Redis.

        Args:
            key (str): The cache key to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.redis_client:
            await self.connect()

        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Checks if a key exists in Redis.

        Args:
            key (str): The cache key to check.

        Returns:
            bool: True if key exists, False otherwise.
        """
        if not self.redis_client:
            await self.connect()

        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in Redis: {e}")
            return False

    async def set_json(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Sets a JSON-serializable value in Redis.

        Args:
            key (str): The cache key.
            value (Any): The value to cache (will be JSON serialized).
            ttl (int): Time to live in seconds.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, ttl)
        except Exception as e:
            logger.error(f"Error serializing and setting JSON for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Retrieves and deserializes a JSON value from Redis.

        Args:
            key (str): The cache key.

        Returns:
            Optional[Any]: The deserialized value or None if not found.
        """
        try:
            json_value = await self.get(key)
            if json_value:
                return json.loads(json_value)
            return None
        except Exception as e:
            logger.error(f"Error retrieving and deserializing JSON for key {key}: {e}")
            return None

    async def cache_search_results(
        self, query_hash: str, results: Any, ttl: int = 1800
    ) -> bool:
        """
        Caches search results with a shorter TTL.

        Args:
            query_hash (str): Hash of the search query.
            results (Any): The search results to cache.
            ttl (int): Time to live in seconds (default 30 minutes).

        Returns:
            bool: True if successful, False otherwise.
        """
        cache_key = f"search_results:{query_hash}"
        return await self.set_json(cache_key, results, ttl)

    async def get_cached_search_results(self, query_hash: str) -> Optional[Any]:
        """
        Retrieves cached search results.

        Args:
            query_hash (str): Hash of the search query.

        Returns:
            Optional[Any]: The cached results or None if not found.
        """
        cache_key = f"search_results:{query_hash}"
        return await self.get_json(cache_key)


# Singleton instance
_redis_manager = None


def get_redis_manager() -> RedisManager:
    """
    Returns a singleton Redis manager instance.
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager


# Example usage
async def main():
    redis_manager = get_redis_manager()
    try:
        # Test basic operations
        await redis_manager.set("test_key", "test_value", 60)
        value = await redis_manager.get("test_key")
        print(f"Retrieved value: {value}")

        # Test JSON operations
        test_data = {"embeddings": [0.1, 0.2, 0.3], "metadata": {"source": "test"}}
        await redis_manager.set_json("test_json", test_data, 60)
        retrieved_data = await redis_manager.get_json("test_json")
        print(f"Retrieved JSON: {retrieved_data}")

    finally:
        await redis_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
