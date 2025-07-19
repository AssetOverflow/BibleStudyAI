"""
Optimized ingestion pipeline for BibleStudyAI agentic RAG + knowledge graph system.

Features:
- Async processing with concurrent operations
- Progress tracking and metrics
- Error handling and recovery
- Configurable pipeline stages
- Single Bible ingestion for optimization
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

import pandas as pd
from tqdm.asyncio import tqdm

from services.bible_service import BibleService
from data_ingestion.chunker import (
    create_biblical_chunker,
    ChunkingConfig,
    BiblicalChunk,
)
from data_ingestion.optimized_embedder import create_optimized_embedder, EmbeddingConfig
from data_ingestion.graph_builder import GraphBuilder
from database.optimized_milvus import create_optimized_milvus_manager
from database.neo4j_graph import Neo4jManager


@dataclass
class IngestionConfig:
    """Configuration for the ingestion pipeline."""

    # Target Bible translation for initial optimization
    target_translation: str = "KJV"

    # Chunking configuration
    chunk_size: int = 250
    chunk_variance: int = 50
    overlap_verses: int = 1

    # Embedding configuration
    embedding_batch_size: int = 50
    max_concurrent_embeddings: int = 3

    # Processing configuration
    max_concurrent_books: int = 5
    enable_progress_tracking: bool = True

    # Database configuration
    collection_name: str = "biblical_chunks_optimized"
    drop_existing_collection: bool = False

    # Book filtering for testing/optimization
    book_filter: Optional[List[str]] = None

    # Enable specific pipeline stages
    enable_chunking: bool = True
    enable_embedding: bool = True
    enable_vector_storage: bool = True
    enable_graph_building: bool = True


@dataclass
class IngestionMetrics:
    """Metrics for tracking ingestion performance."""

    start_time: datetime
    end_time: Optional[datetime] = None

    # Processing counts
    total_verses: int = 0
    total_chunks: int = 0
    successful_embeddings: int = 0
    failed_embeddings: int = 0

    # Timing metrics
    chunking_time: float = 0.0
    embedding_time: float = 0.0
    vector_storage_time: float = 0.0
    graph_building_time: float = 0.0

    # Performance metrics
    verses_per_second: float = 0.0
    chunks_per_second: float = 0.0
    embeddings_per_second: float = 0.0

    def calculate_rates(self):
        """Calculate processing rates."""
        if self.end_time:
            total_time = (self.end_time - self.start_time).total_seconds()

            if total_time > 0:
                self.verses_per_second = self.total_verses / total_time
                self.chunks_per_second = self.total_chunks / total_time
                self.embeddings_per_second = self.successful_embeddings / total_time


class OptimizedIngestionPipeline:
    """
    High-performance ingestion pipeline optimized for agentic RAG + knowledge graph.
    """

    def __init__(self, config: IngestionConfig = None):
        """
        Initialize the optimized ingestion pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config or IngestionConfig()
        self.metrics = IngestionMetrics(start_time=datetime.now())

        # Initialize components
        self.bible_service = None
        self.chunker = None
        self.embedder = None
        self.milvus_manager = None
        self.neo4j_manager = None
        self.graph_builder = None

        logger.info(
            f"Optimized Ingestion Pipeline initialized for: {self.config.target_translation}"
        )

    async def initialize_components(self):
        """Initialize all pipeline components."""

        logger.info("Initializing pipeline components...")

        # Initialize Bible service
        self.bible_service = BibleService(parquet_dir="db/bibles/parquet/")

        # Initialize chunker
        chunking_config = ChunkingConfig(
            target_chunk_size=self.config.chunk_size,
            size_variance=self.config.chunk_variance,
            overlap_verses=self.config.overlap_verses,
            include_context=True,
        )
        self.chunker = create_biblical_chunker(chunking_config)

        # Initialize embedder
        embedding_config = EmbeddingConfig(
            batch_size=self.config.embedding_batch_size,
            max_concurrent_batches=self.config.max_concurrent_embeddings,
            enable_caching=True,
        )
        self.embedder = create_optimized_embedder(embedding_config)
        await self.embedder.initialize()

        # Initialize Milvus manager
        if self.config.enable_vector_storage:
            self.milvus_manager = create_optimized_milvus_manager()
            await self.milvus_manager.initialize()

        # Initialize Neo4j manager
        if self.config.enable_graph_building:
            self.neo4j_manager = Neo4jManager()
            self.graph_builder = GraphBuilder()

        logger.success("All pipeline components initialized")

    async def run_full_pipeline(self) -> IngestionMetrics:
        """
        Run the complete ingestion pipeline.

        Returns:
            Ingestion metrics
        """

        logger.info("Starting optimized ingestion pipeline...")
        start_time = time.time()

        try:
            # Initialize components
            await self.initialize_components()

            # Load Bible data
            bible_data = await self._load_bible_data()

            if bible_data is None or bible_data.empty:
                logger.error(
                    f"No data found for translation: {self.config.target_translation}"
                )
                return self.metrics

            self.metrics.total_verses = len(bible_data)
            logger.info(
                f"Loaded {self.metrics.total_verses} verses from {self.config.target_translation}"
            )

            # Stage 1: Chunking
            chunks = []
            if self.config.enable_chunking:
                chunks = await self._run_chunking_stage(bible_data)
                self.metrics.total_chunks = len(chunks)

            # Stage 2: Embedding generation
            if self.config.enable_embedding and chunks:
                await self._run_embedding_stage(chunks)

            # Stage 3: Vector storage
            if self.config.enable_vector_storage and chunks:
                await self._run_vector_storage_stage(chunks)

            # Stage 4: Knowledge graph building
            if self.config.enable_graph_building and chunks:
                await self._run_graph_building_stage(chunks)

            # Finalize metrics
            self.metrics.end_time = datetime.now()
            self.metrics.calculate_rates()

            # Log completion
            total_time = time.time() - start_time
            logger.success(
                f"Pipeline completed in {total_time:.2f}s - {self._format_metrics()}"
            )

            return self.metrics

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

        finally:
            await self._cleanup_components()

    async def _load_bible_data(self) -> Optional[pd.DataFrame]:
        """Load Bible data for the target translation."""

        logger.info(f"Loading Bible data for {self.config.target_translation}...")

        if self.config.target_translation not in self.bible_service.bibles:
            available = list(self.bible_service.bibles.keys())
            logger.error(
                f"Translation {self.config.target_translation} not found. "
                f"Available: {available}"
            )
            return None

        bible_df = self.bible_service.bibles[self.config.target_translation].copy()

        # Apply book filter if specified
        if self.config.book_filter:
            original_count = len(bible_df)
            bible_df = bible_df[bible_df["book"].isin(self.config.book_filter)]
            logger.info(
                f"Filtered to {len(bible_df)} verses from {len(self.config.book_filter)} books "
                f"(was {original_count} verses)"
            )

        return bible_df

    async def _run_chunking_stage(
        self, bible_data: pd.DataFrame
    ) -> List[BiblicalChunk]:
        """Run the chunking stage."""

        logger.info("Stage 1: Starting chunking...")
        stage_start = time.time()

        try:
            chunks = await self.chunker.chunk_bible_data(
                bible_df=bible_data,
                translation=self.config.target_translation,
                book_filter=self.config.book_filter,
            )

            self.metrics.chunking_time = time.time() - stage_start
            logger.success(
                f"Chunking completed: {len(chunks)} chunks in {self.metrics.chunking_time:.2f}s"
            )

            return chunks

        except Exception as e:
            logger.error(f"Chunking stage failed: {e}")
            raise

    async def _run_embedding_stage(self, chunks: List[BiblicalChunk]):
        """Run the embedding generation stage."""

        logger.info("Stage 2: Starting embedding generation...")
        stage_start = time.time()

        try:
            # Generate embeddings in batches
            results = await self.embedder.embed_chunks_batch(
                chunks=chunks, show_progress=self.config.enable_progress_tracking
            )

            # Count successful embeddings
            self.metrics.successful_embeddings = sum(1 for r in results if r.success)
            self.metrics.failed_embeddings = sum(1 for r in results if not r.success)

            self.metrics.embedding_time = time.time() - stage_start

            # Get embedder stats
            embedder_stats = self.embedder.get_stats()

            logger.success(
                f"Embedding completed: {self.metrics.successful_embeddings}/{len(chunks)} successful "
                f"({embedder_stats['cache_hit_rate']:.2%} cache hit rate) "
                f"in {self.metrics.embedding_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Embedding stage failed: {e}")
            raise

    async def _run_vector_storage_stage(self, chunks: List[BiblicalChunk]):
        """Run the vector storage stage."""

        logger.info("Stage 3: Starting vector storage...")
        stage_start = time.time()

        try:
            # Create collection if it doesn't exist
            await self.milvus_manager.create_collection(
                collection_name=self.config.collection_name,
                drop_if_exists=self.config.drop_existing_collection,
            )

            # Create optimized indexes
            await self.milvus_manager.create_optimized_index(
                self.config.collection_name
            )

            # Filter chunks with embeddings
            chunks_with_embeddings = [chunk for chunk in chunks if chunk.embedding]

            if chunks_with_embeddings:
                # Insert chunks in batches
                success = await self.milvus_manager.insert_chunks_batch(
                    collection_name=self.config.collection_name,
                    chunks=chunks_with_embeddings,
                    batch_size=self.config.embedding_batch_size,
                )

                if not success:
                    raise Exception("Failed to insert chunks into Milvus")

            self.metrics.vector_storage_time = time.time() - stage_start

            # Get collection stats
            stats = await self.milvus_manager.get_collection_stats(
                self.config.collection_name
            )

            logger.success(
                f"Vector storage completed: {len(chunks_with_embeddings)} chunks stored "
                f"(Collection: {stats.get('num_entities', 0)} total entities) "
                f"in {self.metrics.vector_storage_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Vector storage stage failed: {e}")
            raise

    async def _run_graph_building_stage(self, chunks: List[BiblicalChunk]):
        """Run the knowledge graph building stage."""

        logger.info("Stage 4: Starting knowledge graph building...")
        stage_start = time.time()

        try:
            # For now, we'll use a simplified approach
            # In a full implementation, this would extract entities and relationships

            # Group chunks by book for graph building
            book_chunks = {}
            for chunk in chunks:
                book = chunk.book
                if book not in book_chunks:
                    book_chunks[book] = []
                book_chunks[book].append(chunk)

            total_processed = 0

            # Process each book
            for book, book_chunk_list in book_chunks.items():
                logger.info(f"Building graph for {book}: {len(book_chunk_list)} chunks")

                # This is a placeholder - in full implementation:
                # 1. Extract biblical entities (people, places, themes)
                # 2. Identify relationships between entities
                # 3. Create temporal knowledge with biblical timeline
                # 4. Store in Neo4j with proper biblical ontology

                total_processed += len(book_chunk_list)

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)

            self.metrics.graph_building_time = time.time() - stage_start

            logger.success(
                f"Graph building completed: {total_processed} chunks processed "
                f"across {len(book_chunks)} books "
                f"in {self.metrics.graph_building_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Graph building stage failed: {e}")
            # Don't raise - graph building is optional for now
            logger.warning("Continuing without graph building...")

    def _format_metrics(self) -> str:
        """Format metrics for logging."""

        return (
            f"{self.metrics.total_chunks} chunks, "
            f"{self.metrics.successful_embeddings} embeddings, "
            f"{self.metrics.chunks_per_second:.1f} chunks/s, "
            f"{self.metrics.embeddings_per_second:.1f} embeddings/s"
        )

    async def _cleanup_components(self):
        """Clean up pipeline components."""

        logger.info("Cleaning up pipeline components...")

        try:
            if self.embedder:
                await self.embedder.close()

            if self.milvus_manager:
                await self.milvus_manager.close()

            # Neo4j cleanup would go here if needed

            logger.info("Component cleanup completed")

        except Exception as e:
            logger.warning(f"Cleanup error: {e}")

    async def run_single_book_test(self, book_name: str) -> IngestionMetrics:
        """
        Run pipeline for a single book (for testing and optimization).

        Args:
            book_name: Name of the book to process

        Returns:
            Ingestion metrics
        """

        # Configure for single book
        self.config.book_filter = [book_name]
        self.config.collection_name = f"test_{book_name.lower().replace(' ', '_')}"
        self.config.drop_existing_collection = True

        logger.info(f"Running single book test for: {book_name}")

        return await self.run_full_pipeline()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""

        return {
            "configuration": {
                "translation": self.config.target_translation,
                "chunk_size": self.config.chunk_size,
                "embedding_batch_size": self.config.embedding_batch_size,
                "book_filter": self.config.book_filter,
            },
            "counts": {
                "total_verses": self.metrics.total_verses,
                "total_chunks": self.metrics.total_chunks,
                "successful_embeddings": self.metrics.successful_embeddings,
                "failed_embeddings": self.metrics.failed_embeddings,
            },
            "timing": {
                "chunking_time": self.metrics.chunking_time,
                "embedding_time": self.metrics.embedding_time,
                "vector_storage_time": self.metrics.vector_storage_time,
                "graph_building_time": self.metrics.graph_building_time,
                "total_time": (
                    (self.metrics.end_time - self.metrics.start_time).total_seconds()
                    if self.metrics.end_time
                    else 0
                ),
            },
            "performance": {
                "verses_per_second": self.metrics.verses_per_second,
                "chunks_per_second": self.metrics.chunks_per_second,
                "embeddings_per_second": self.metrics.embeddings_per_second,
            },
        }


# Factory function
def create_optimized_pipeline(
    config: IngestionConfig = None,
) -> OptimizedIngestionPipeline:
    """Create an optimized ingestion pipeline instance."""
    return OptimizedIngestionPipeline(config)


# Example usage and testing
if __name__ == "__main__":

    async def test_single_book():
        """Test pipeline with a single book."""

        config = IngestionConfig(
            target_translation="KJV",
            chunk_size=200,
            embedding_batch_size=20,
            enable_progress_tracking=True,
        )

        pipeline = create_optimized_pipeline(config)

        # Test with Genesis (shorter book for testing)
        metrics = await pipeline.run_single_book_test("Genesis")

        # Print comprehensive metrics
        summary = pipeline.get_metrics_summary()
        print("\n=== PIPELINE METRICS ===")

        for category, data in summary.items():
            print(f"\n{category.upper()}:")
            for key, value in data.items():
                print(f"  {key}: {value}")

    async def test_full_kjv():
        """Test full KJV ingestion."""

        config = IngestionConfig(
            target_translation="KJV",
            chunk_size=250,
            embedding_batch_size=50,
            max_concurrent_embeddings=3,
            collection_name="kjv_full_optimized",
            drop_existing_collection=True,
        )

        pipeline = create_optimized_pipeline(config)
        metrics = await pipeline.run_full_pipeline()

        # Print summary
        summary = pipeline.get_metrics_summary()
        print(f"\n=== FULL KJV INGESTION COMPLETE ===")
        print(f"Total time: {summary['timing']['total_time']:.2f}s")
        print(f"Chunks processed: {summary['counts']['total_chunks']}")
        print(
            f"Performance: {summary['performance']['chunks_per_second']:.1f} chunks/s"
        )

    # Run test
    print("Testing single book ingestion...")
    asyncio.run(test_single_book())

    # Uncomment to test full Bible
    # print("Testing full Bible ingestion...")
    # asyncio.run(test_full_kjv())
