"""
Optimized embedder for BibleStudyAI with async batching and caching.

Features:
- Async batch processing for high throughput
- Redis caching with TTL
- Multiple provider support (OpenAI, Anthropic, XAI)
- Rate limiting and retry logic
- Progress tracking and metrics
"""

import asyncio
import json
import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
from loguru import logger

from services.ai_integration import ai_integration_client, ModelProvider
from data_ingestion.chunker import BiblicalChunk


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""

    provider: ModelProvider = ModelProvider.OPENAI
    model: str = "text-embedding-3-small"
    batch_size: int = 100
    max_concurrent_batches: int = 5
    rate_limit_delay: float = 0.1  # seconds between batches
    cache_ttl: int = 86400 * 7  # 7 days
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True


@dataclass
class EmbeddingResult:
    """Result of embedding operation."""

    chunk_id: str
    embedding: Optional[List[float]]
    success: bool
    error: Optional[str] = None
    cache_hit: bool = False
    processing_time: float = 0.0


class OptimizedEmbedder:
    """
    High-performance embedder with async batching and intelligent caching.
    """

    def __init__(self, config: EmbeddingConfig = None):
        """
        Initialize the optimized embedder.

        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self._redis_manager = None
        self._rate_limiter = asyncio.Semaphore(self.config.max_concurrent_batches)
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "total_processing_time": 0.0,
        }

        logger.info(f"Optimized Embedder initialized: {self.config}")

    async def initialize(self):
        """Initialize Redis connection for caching."""
        if self.config.enable_caching:
            try:
                from database.redis_cache import RedisManager

                self._redis_manager = RedisManager()
                logger.info("Redis caching enabled for embeddings")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis caching: {e}")
                self._redis_manager = None

    async def embed_chunks_batch(
        self, chunks: List[BiblicalChunk], show_progress: bool = True
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for a batch of chunks with optimization.

        Args:
            chunks: List of BiblicalChunk objects
            show_progress: Whether to show progress logging

        Returns:
            List of EmbeddingResult objects
        """

        if not chunks:
            return []

        start_time = time.time()
        logger.info(f"Starting batch embedding for {len(chunks)} chunks")

        # Check cache first if enabled
        cache_results = {}
        chunks_to_process = []

        if self.config.enable_caching and self._redis_manager:
            cache_results, chunks_to_process = await self._check_cache_batch(chunks)

            if cache_results:
                logger.info(
                    f"Cache hits: {len(cache_results)}, "
                    f"Need to process: {len(chunks_to_process)}"
                )
        else:
            chunks_to_process = chunks

        # Process remaining chunks in batches
        processing_results = []
        if chunks_to_process:
            processing_results = await self._process_chunks_concurrent(
                chunks_to_process, show_progress
            )

        # Combine cache hits and processing results
        all_results = []

        # Add cache hits
        for chunk in chunks:
            if chunk.id in cache_results:
                result = EmbeddingResult(
                    chunk_id=chunk.id,
                    embedding=cache_results[chunk.id],
                    success=True,
                    cache_hit=True,
                    processing_time=0.0,
                )
                all_results.append(result)

        # Add processing results
        all_results.extend(processing_results)

        # Sort results to match input order
        chunk_id_to_index = {chunk.id: i for i, chunk in enumerate(chunks)}
        all_results.sort(key=lambda x: chunk_id_to_index.get(x.chunk_id, 999999))

        # Update chunks with embeddings
        for i, result in enumerate(all_results):
            if result.success and i < len(chunks):
                chunks[i].embedding = result.embedding

        # Update statistics
        processing_time = time.time() - start_time
        self._update_stats(all_results, processing_time)

        # Log summary
        successful = sum(1 for r in all_results if r.success)
        cache_hits = sum(1 for r in all_results if r.cache_hit)

        logger.success(
            f"Batch embedding completed: {successful}/{len(chunks)} successful, "
            f"{cache_hits} cache hits, {processing_time:.2f}s total"
        )

        return all_results

    async def _check_cache_batch(
        self, chunks: List[BiblicalChunk]
    ) -> Tuple[Dict[str, List[float]], List[BiblicalChunk]]:
        """
        Check cache for existing embeddings.

        Args:
            chunks: List of chunks to check

        Returns:
            Tuple of (cache_results, chunks_to_process)
        """

        cache_results = {}
        chunks_to_process = []

        if not self._redis_manager:
            return cache_results, chunks

        try:
            # Prepare cache keys
            cache_keys = []
            for chunk in chunks:
                cache_key = self._generate_cache_key(chunk.content)
                cache_keys.append((chunk.id, cache_key))

            # Batch check cache
            cached_embeddings = await self._redis_manager.mget(
                [key for _, key in cache_keys]
            )

            for i, ((chunk_id, cache_key), cached_data) in enumerate(
                zip(cache_keys, cached_embeddings)
            ):
                if cached_data:
                    try:
                        embedding = json.loads(cached_data)
                        cache_results[chunk_id] = embedding
                    except (json.JSONDecodeError, TypeError):
                        chunks_to_process.append(chunks[i])
                else:
                    chunks_to_process.append(chunks[i])

        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            chunks_to_process = chunks

        return cache_results, chunks_to_process

    async def _process_chunks_concurrent(
        self, chunks: List[BiblicalChunk], show_progress: bool = True
    ) -> List[EmbeddingResult]:
        """
        Process chunks concurrently with rate limiting.

        Args:
            chunks: Chunks to process
            show_progress: Whether to show progress

        Returns:
            List of EmbeddingResult objects
        """

        # Split into batches
        batches = [
            chunks[i : i + self.config.batch_size]
            for i in range(0, len(chunks), self.config.batch_size)
        ]

        logger.info(f"Processing {len(chunks)} chunks in {len(batches)} batches")

        # Process batches concurrently
        tasks = []
        for i, batch in enumerate(batches):
            task = self._process_single_batch(batch, i + 1, len(batches))
            tasks.append(task)

        # Gather results
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results
        all_results = []
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch processing failed: {batch_result}")
                continue
            all_results.extend(batch_result)

        return all_results

    async def _process_single_batch(
        self, batch: List[BiblicalChunk], batch_num: int, total_batches: int
    ) -> List[EmbeddingResult]:
        """
        Process a single batch of chunks.

        Args:
            batch: Chunks to process
            batch_num: Current batch number
            total_batches: Total number of batches

        Returns:
            List of EmbeddingResult objects
        """

        async with self._rate_limiter:
            batch_start = time.time()

            try:
                # Extract texts
                texts = [chunk.content for chunk in batch]

                # Generate embeddings with retry
                embeddings = await self._generate_embeddings_with_retry(texts)

                # Create results
                results = []
                for i, chunk in enumerate(batch):
                    if i < len(embeddings) and embeddings[i] is not None:
                        result = EmbeddingResult(
                            chunk_id=chunk.id,
                            embedding=embeddings[i],
                            success=True,
                            processing_time=time.time() - batch_start,
                        )

                        # Cache the embedding
                        if self.config.enable_caching and self._redis_manager:
                            await self._cache_embedding(chunk.content, embeddings[i])

                    else:
                        result = EmbeddingResult(
                            chunk_id=chunk.id,
                            embedding=None,
                            success=False,
                            error="Failed to generate embedding",
                            processing_time=time.time() - batch_start,
                        )

                    results.append(result)

                batch_time = time.time() - batch_start
                logger.info(
                    f"Batch {batch_num}/{total_batches} completed: "
                    f"{len(batch)} chunks in {batch_time:.2f}s"
                )

                # Rate limiting delay
                if batch_num < total_batches:
                    await asyncio.sleep(self.config.rate_limit_delay)

                return results

            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}")

                # Return error results for all chunks in batch
                return [
                    EmbeddingResult(
                        chunk_id=chunk.id,
                        embedding=None,
                        success=False,
                        error=str(e),
                        processing_time=time.time() - batch_start,
                    )
                    for chunk in batch
                ]

    async def _generate_embeddings_with_retry(
        self, texts: List[str]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings with retry logic.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (None for failures)
        """

        for attempt in range(self.config.retry_attempts):
            try:
                # Generate embeddings using AI integration
                embeddings = []

                for text in texts:
                    embedding = await ai_integration_client.get_embedding(
                        text=text,
                        provider=self.config.provider,
                        model=self.config.model,
                    )
                    embeddings.append(embedding)

                return embeddings

            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")

                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                else:
                    logger.error(f"All embedding attempts failed for batch")
                    return [None] * len(texts)

        return [None] * len(texts)

    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text."""

        # Include provider and model in key for uniqueness
        key_data = f"{self.config.provider.value}:{self.config.model}:{text}"
        return f"embedding:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def _cache_embedding(self, text: str, embedding: List[float]):
        """Cache embedding in Redis."""

        if not self._redis_manager:
            return

        try:
            cache_key = self._generate_cache_key(text)
            cache_value = json.dumps(embedding)

            await self._redis_manager.set(cache_key, cache_value, self.config.cache_ttl)

        except Exception as e:
            logger.debug(f"Failed to cache embedding: {e}")

    def _update_stats(self, results: List[EmbeddingResult], processing_time: float):
        """Update processing statistics."""

        self._stats["total_requests"] += len(results)
        self._stats["cache_hits"] += sum(1 for r in results if r.cache_hit)
        self._stats["cache_misses"] += sum(
            1 for r in results if not r.cache_hit and r.success
        )
        self._stats["errors"] += sum(1 for r in results if not r.success)
        self._stats["total_processing_time"] += processing_time

    def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""

        stats = self._stats.copy()

        if stats["total_requests"] > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_requests"]
            stats["error_rate"] = stats["errors"] / stats["total_requests"]
            stats["avg_processing_time"] = (
                stats["total_processing_time"] / stats["total_requests"]
            )
        else:
            stats["cache_hit_rate"] = 0.0
            stats["error_rate"] = 0.0
            stats["avg_processing_time"] = 0.0

        return stats

    async def embed_single_text(
        self, text: str, use_cache: bool = True
    ) -> Optional[List[float]]:
        """
        Embed a single text (for testing or ad-hoc use).

        Args:
            text: Text to embed
            use_cache: Whether to use caching

        Returns:
            Embedding vector or None if failed
        """

        # Check cache first
        if use_cache and self.config.enable_caching and self._redis_manager:
            cache_key = self._generate_cache_key(text)
            cached_data = await self._redis_manager.get(cache_key)

            if cached_data:
                try:
                    return json.loads(cached_data)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Generate embedding
        try:
            embedding = await ai_integration_client.get_embedding(
                text=text, provider=self.config.provider, model=self.config.model
            )

            # Cache result
            if (
                use_cache
                and embedding
                and self.config.enable_caching
                and self._redis_manager
            ):
                await self._cache_embedding(text, embedding)

            return embedding

        except Exception as e:
            logger.error(f"Failed to embed single text: {e}")
            return None

    async def close(self):
        """Clean up resources."""
        if self._redis_manager:
            # Redis manager cleanup is handled elsewhere
            pass


# Factory function
def create_optimized_embedder(config: EmbeddingConfig = None) -> OptimizedEmbedder:
    """Create an optimized embedder instance."""
    return OptimizedEmbedder(config)


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    from data_ingestion.chunker import create_biblical_chunker, ChunkingConfig

    async def test_embedder():
        """Test the optimized embedder."""

        # Create sample data
        sample_data = {
            "translation": ["KJV"] * 3,
            "book": ["Genesis"] * 3,
            "chapter": [1] * 3,
            "verse": [1, 2, 3],
            "text": [
                "In the beginning God created the heaven and the earth.",
                "And the earth was without form, and void; and darkness was upon the face of the deep.",
                "And the Spirit of God moved upon the face of the waters.",
            ],
            "cross_references": [[], [], []],
            "strongs_numbers": [None] * 3,
        }

        df = pd.DataFrame(sample_data)

        # Create chunks
        chunker = create_biblical_chunker(ChunkingConfig(target_chunk_size=50))
        chunks = await chunker.chunk_bible_data(df, "KJV")

        # Create embedder
        config = EmbeddingConfig(batch_size=2, max_concurrent_batches=2)
        embedder = create_optimized_embedder(config)
        await embedder.initialize()

        # Generate embeddings
        results = await embedder.embed_chunks_batch(chunks)

        # Print results
        for result in results:
            print(
                f"Chunk {result.chunk_id}: "
                f"Success={result.success}, "
                f"Cache Hit={result.cache_hit}, "
                f"Time={result.processing_time:.3f}s"
            )

        # Print stats
        stats = embedder.get_stats()
        print(f"\nEmbedding Stats: {stats}")

        await embedder.close()

    # Run test
    asyncio.run(test_embedder())
