#!/usr/bin/env python3
"""
Genesis ingestion test with optimized pipeline - Fixed paths.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root
project_root = Path(__file__).parent.absolute()
print(f"Project root: {project_root}")

# Load environment variables from backend directory
env_file = project_root / "backend" / ".env"
print(f"Loading environment from: {env_file}")
load_dotenv(env_file)

# Override Milvus and Redis hosts for local testing (Docker host vs container name)
os.environ["MILVUS_HOST"] = "localhost"
os.environ["REDIS_URL"] = "redis://localhost:6379"
print(f"Milvus host set to: {os.getenv('MILVUS_HOST')}")
print(f"Redis URL set to: {os.getenv('REDIS_URL')}")

# Add backend to path but don't change working directory
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from data_ingestion.optimized_pipeline import create_optimized_pipeline, IngestionConfig
from loguru import logger


async def test_genesis_full_pipeline():
    """Test the complete optimized pipeline with Genesis."""

    logger.info("🚀 Starting Genesis ingestion with optimized pipeline...")

    # Bible data is in project root, not backend
    bible_data_dir = project_root / "db" / "bibles" / "parquet"
    print(f"Bible data directory: {bible_data_dir}")
    print(f"Bible data exists: {bible_data_dir.exists()}")

    if bible_data_dir.exists():
        files = list(bible_data_dir.glob("*.parquet"))
        print(f"Found {len(files)} Bible files:")
        for f in files[:3]:  # Show first 3
            print(f"  - {f.name}")

    # Change to project root so relative paths work correctly
    original_cwd = os.getcwd()
    os.chdir(project_root)
    logger.info(f"Changed working directory to: {project_root}")

    # Configure for Genesis book
    config = IngestionConfig(
        target_translation="KJV",
        chunk_size=500,
        chunk_variance=50,
        overlap_verses=1,
        embedding_batch_size=32,
        max_concurrent_embeddings=3,
        enable_progress_tracking=True,
        book_filter=["Genesis"],  # This is the correct parameter name
    )

    try:
        # Create optimized pipeline
        logger.info("Creating optimized pipeline...")
        pipeline = create_optimized_pipeline(config)

        # Initialize components
        logger.info("Initializing pipeline components...")
        await pipeline.initialize_components()

        # Test the ingestion
        logger.info("Starting Genesis ingestion...")
        results = await pipeline.run_full_pipeline()

        # Display results
        if results:
            # Calculate total time
            total_time = (
                (results.end_time - results.start_time).total_seconds()
                if results.end_time
                else 0
            )

            logger.success(f"✅ Genesis ingestion completed:")
            logger.info(f"   📚 Chunks processed: {results.total_chunks}")
            logger.info(f"   📖 Verses processed: {results.total_verses}")
            logger.info(f"   ⏱️  Total time: {total_time:.2f}s")
            logger.info(f"   🚀 Chunks/second: {results.chunks_per_second:.1f}")
            logger.info(
                f"   ⚡ Embeddings: {results.successful_embeddings}/{results.successful_embeddings + results.failed_embeddings}"
            )

        # Test search functionality
        logger.info("Testing vector search...")

        # Re-initialize connection since pipeline cleans up automatically
        await pipeline.milvus_manager.initialize()

        # Generate embedding for the query using the pipeline's embedder
        query_text = "In the beginning God created"
        query_embedding = await pipeline.embedder.embed_single_text(query_text)

        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return False

        # Use hybrid_search with the generated embedding and correct collection name
        search_results = await pipeline.milvus_manager.hybrid_search(
            collection_name=pipeline.config.collection_name,  # Use the actual collection name
            query_embedding=query_embedding,
            query_text=query_text,
            limit=3,
        )

        logger.info(f"Found {len(search_results)} search results:")
        for i, result in enumerate(search_results, 1):
            logger.info(f"  {i}. Score: {result.get('score', 0):.3f}")
            logger.info(f"     Text: {result.get('text', '')[:100]}...")
            logger.info(f"     Book: {result.get('book', 'Unknown')}")
            logger.info(f"     Chapter: {result.get('chapter', 'Unknown')}")

        logger.success("🎉 Genesis pipeline test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        logger.exception("Full error details:")
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        # Cleanup
        if "pipeline" in locals():
            await pipeline._cleanup_components()


async def main():
    """Main test function."""
    print("=" * 60)
    print("🔬 GENESIS PIPELINE TEST - OPTIMIZED VERSION")
    print("=" * 60)

    # Verify environment
    required_vars = ["OPENAI_API_KEY", "MILVUS_HOST", "REDIS_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False

    logger.info("✅ Environment variables loaded successfully")
    logger.info(f"OpenAI API Key: {'*' * 20}...{os.getenv('OPENAI_API_KEY', '')[-4:]}")
    logger.info(f"Milvus Host: {os.getenv('MILVUS_HOST')}")
    logger.info(f"Redis URL: {os.getenv('REDIS_URL')}")

    # Run the test
    success = await test_genesis_full_pipeline()

    if success:
        print("\n" + "=" * 60)
        print("🎊 ALL TESTS PASSED! Ready for production!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED! Check logs above.")
        print("=" * 60)

    return success


if __name__ == "__main__":
    asyncio.run(main())
