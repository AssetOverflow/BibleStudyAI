#!/usr/bin/env python3
"""
Test script for optimized BibleStudyAI ingestion pipeline.

Run this to test the new chunking, embedding, and storage system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set up environment
os.chdir(backend_path)

from data_ingestion.optimized_pipeline import create_optimized_pipeline, IngestionConfig
from loguru import logger


async def test_genesis_ingestion():
    """Test ingestion with just the book of Genesis."""

    logger.info("🚀 Testing optimized ingestion pipeline with Genesis...")

    # Configure for Genesis only (faster testing)
    config = IngestionConfig(
        target_translation="KJV",
        chunk_size=200,
        chunk_variance=30,
        overlap_verses=1,
        embedding_batch_size=10,  # Smaller batches for testing
        max_concurrent_embeddings=2,
        book_filter=["Genesis"],  # Only Genesis for testing
        collection_name="genesis_test_optimized",
        drop_existing_collection=True,
        enable_progress_tracking=True,
    )

    # Create and run pipeline
    pipeline = create_optimized_pipeline(config)

    try:
        metrics = await pipeline.run_full_pipeline()

        # Print results
        summary = pipeline.get_metrics_summary()

        print("\n" + "=" * 60)
        print("🎉 GENESIS INGESTION TEST COMPLETED!")
        print("=" * 60)

        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   Translation: {summary['configuration']['translation']}")
        print(f"   Books: {summary['configuration']['book_filter']}")
        print(f"   Verses processed: {summary['counts']['total_verses']}")
        print(f"   Chunks created: {summary['counts']['total_chunks']}")
        print(f"   Embeddings generated: {summary['counts']['successful_embeddings']}")
        print(f"   Failed embeddings: {summary['counts']['failed_embeddings']}")

        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   Total time: {summary['timing']['total_time']:.2f}s")
        print(f"   Chunking time: {summary['timing']['chunking_time']:.2f}s")
        print(f"   Embedding time: {summary['timing']['embedding_time']:.2f}s")
        print(
            f"   Vector storage time: {summary['timing']['vector_storage_time']:.2f}s"
        )
        print(
            f"   Graph building time: {summary['timing']['graph_building_time']:.2f}s"
        )

        print(f"\n🚀 THROUGHPUT:")
        print(f"   Verses/second: {summary['performance']['verses_per_second']:.1f}")
        print(f"   Chunks/second: {summary['performance']['chunks_per_second']:.1f}")
        print(
            f"   Embeddings/second: {summary['performance']['embeddings_per_second']:.1f}"
        )

        success_rate = (
            summary["counts"]["successful_embeddings"]
            / summary["counts"]["total_chunks"]
        )
        print(f"\n✅ SUCCESS RATE: {success_rate:.1%}")

        if success_rate > 0.95:
            print("🎯 EXCELLENT: Pipeline is working optimally!")
        elif success_rate > 0.8:
            print("✅ GOOD: Pipeline is working well with minor issues")
        else:
            print("⚠️  WARNING: Pipeline has some issues to address")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_chunker_only():
    """Test just the chunker component."""

    logger.info("🧪 Testing chunker component only...")

    try:
        from services.bible_service import BibleService
        from data_ingestion.chunker import create_biblical_chunker, ChunkingConfig

        # Load Bible data
        bible_service = BibleService(parquet_dir="db/bibles/parquet/")

        if "KJV" not in bible_service.bibles:
            logger.error("KJV not found in Bible data")
            return False

        # Get Genesis data
        bible_df = bible_service.bibles["KJV"]
        genesis_df = bible_df[bible_df["book"] == "Genesis"].head(
            20
        )  # Just first 20 verses

        # Create chunker
        config = ChunkingConfig(target_chunk_size=100, size_variance=20)
        chunker = create_biblical_chunker(config)

        # Chunk data
        chunks = await chunker.chunk_bible_data(genesis_df, "KJV")

        print(f"\n🧪 CHUNKER TEST RESULTS:")
        print(f"   Input verses: {len(genesis_df)}")
        print(f"   Output chunks: {len(chunks)}")

        if chunks:
            print(f"\n📄 SAMPLE CHUNK:")
            sample = chunks[0]
            print(f"   ID: {sample.id}")
            print(f"   Reference: {sample.metadata['passage_reference']}")
            print(f"   Word count: {sample.word_count}")
            print(f"   Content: {sample.content[:100]}...")
            print(f"   Metadata keys: {list(sample.metadata.keys())}")

            print("✅ Chunker test passed!")
            return True
        else:
            print("❌ No chunks created")
            return False

    except Exception as e:
        logger.error(f"❌ Chunker test failed: {e}")
        return False


async def main():
    """Run all tests."""

    print("🔧 BibleStudyAI Optimized Pipeline Test Suite")
    print("=" * 50)

    # Test 1: Chunker only
    print("\n1️⃣ Testing chunker component...")
    chunker_success = await test_chunker_only()

    if not chunker_success:
        print("❌ Chunker test failed. Fix before proceeding.")
        return

    # Test 2: Full pipeline with Genesis
    print("\n2️⃣ Testing full pipeline with Genesis...")
    pipeline_success = await test_genesis_ingestion()

    if pipeline_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🚀 Your optimized RAG + Knowledge Graph pipeline is ready!")
        print("\n📋 NEXT STEPS:")
        print("   1. Fix any entity extraction issues in agents/tools.py")
        print("   2. Implement Pydantic AI agent framework")
        print("   3. Add biblical entity patterns and tools")
        print("   4. Test with full Bible when ready")
    else:
        print("\n❌ TESTS FAILED - Check errors above")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
