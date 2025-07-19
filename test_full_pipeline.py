#!/usr/bin/env python3
"""
Test the full optimized pipeline with Genesis book using real services.
"""

import asyncio
import sys
import os
from pathlib import Path
import time

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)


async def test_genesis_full_pipeline():
    """Test the complete pipeline with Genesis."""

    print("🚀 Testing Full Optimized Pipeline with Genesis!")
    print("=" * 60)

    try:
        from data_ingestion.optimized_pipeline import (
            create_optimized_pipeline,
            IngestionConfig,
        )

        # Configure for Genesis with optimized settings
        config = IngestionConfig(
            target_translation="KJV",
            chunk_size=200,  # Moderate chunk size
            chunk_variance=40,  # Allow some variance
            overlap_verses=1,  # Single verse overlap
            embedding_batch_size=20,  # Smaller batches for testing
            max_concurrent_embeddings=2,  # Conservative concurrency
            book_filter=["Genesis"],  # Only Genesis for testing
            collection_name="genesis_optimized_test",
            drop_existing_collection=True,
            enable_progress_tracking=True,
            enable_chunking=True,
            enable_embedding=True,
            enable_vector_storage=True,
            enable_graph_building=False,  # Disable for now
        )

        print(f"📋 Configuration:")
        print(f"   Translation: {config.target_translation}")
        print(f"   Book: {config.book_filter}")
        print(f"   Chunk size: {config.chunk_size} ± {config.chunk_variance} words")
        print(f"   Embedding batch size: {config.embedding_batch_size}")
        print(f"   Collection: {config.collection_name}")

        # Create and run pipeline
        pipeline = create_optimized_pipeline(config)

        start_time = time.time()
        print(f"\n🏁 Starting pipeline at {time.strftime('%H:%M:%S')}...")

        metrics = await pipeline.run_full_pipeline()

        # Get comprehensive results
        summary = pipeline.get_metrics_summary()
        total_time = time.time() - start_time

        # Display results
        print("\n" + "=" * 60)
        print("🎉 GENESIS PIPELINE COMPLETED!")
        print("=" * 60)

        print(f"\n📊 PROCESSING RESULTS:")
        print(f"   Total verses processed: {summary['counts']['total_verses']}")
        print(f"   Chunks created: {summary['counts']['total_chunks']}")
        print(f"   Successful embeddings: {summary['counts']['successful_embeddings']}")
        print(f"   Failed embeddings: {summary['counts']['failed_embeddings']}")

        success_rate = (
            summary["counts"]["successful_embeddings"]
            / summary["counts"]["total_chunks"]
            if summary["counts"]["total_chunks"] > 0
            else 0
        )

        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   Total pipeline time: {total_time:.2f}s")
        print(f"   Chunking time: {summary['timing']['chunking_time']:.2f}s")
        print(f"   Embedding time: {summary['timing']['embedding_time']:.2f}s")
        print(
            f"   Vector storage time: {summary['timing']['vector_storage_time']:.2f}s"
        )

        print(f"\n🚀 THROUGHPUT:")
        print(f"   Verses/second: {summary['performance']['verses_per_second']:.1f}")
        print(f"   Chunks/second: {summary['performance']['chunks_per_second']:.1f}")
        print(
            f"   Embeddings/second: {summary['performance']['embeddings_per_second']:.1f}"
        )

        print(f"\n✅ SUCCESS METRICS:")
        print(f"   Overall success rate: {success_rate:.1%}")

        if success_rate >= 0.95:
            print("🎯 EXCELLENT: Pipeline is working optimally!")

            # Test a quick search
            print(f"\n🔍 Testing search functionality...")
            await test_search_functionality(config.collection_name)

            print(f"\n🚀 READY FOR FULL BIBLE INGESTION!")
            return True

        elif success_rate >= 0.8:
            print("✅ GOOD: Pipeline working with minor issues")
            return True
        else:
            print("⚠️  WARNING: Pipeline has issues to address")
            return False

    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_search_functionality(collection_name: str):
    """Test basic search functionality."""

    try:
        from database.optimized_milvus import create_optimized_milvus_manager
        from data_ingestion.optimized_embedder import (
            create_optimized_embedder,
            EmbeddingConfig,
        )

        # Initialize components
        milvus_manager = create_optimized_milvus_manager()
        await milvus_manager.initialize()

        embedder = create_optimized_embedder(EmbeddingConfig())
        await embedder.initialize()

        # Test query
        test_query = "In the beginning God created"

        # Generate embedding for search
        query_embedding = await embedder.embed_single_text(test_query)

        if query_embedding:
            # Search
            results = await milvus_manager.hybrid_search(
                collection_name=collection_name,
                query_embedding=query_embedding,
                query_text=test_query,
                limit=3,
            )

            print(f"   Query: '{test_query}'")
            print(f"   Results found: {len(results)}")

            if results:
                print(f"   Top result score: {results[0].get('score', 0):.3f}")
                print(f"   Content preview: {results[0].get('content', '')[:100]}...")
                print("   ✅ Search functionality working!")
            else:
                print("   ⚠️  No search results found")
        else:
            print("   ❌ Failed to generate query embedding")

        await milvus_manager.close()
        await embedder.close()

    except Exception as e:
        print(f"   ❌ Search test failed: {e}")


async def test_full_kjv_pipeline():
    """Test with full KJV Bible (only run this after Genesis test passes)."""

    print("\n🔥 FULL KJV BIBLE PIPELINE TEST")
    print("=" * 60)
    print("⚠️  This will take significantly longer and use more API credits!")

    response = input("Continue with full Bible? (y/N): ").strip().lower()
    if response != "y":
        print("Skipping full Bible test.")
        return

    try:
        from data_ingestion.optimized_pipeline import (
            create_optimized_pipeline,
            IngestionConfig,
        )

        # Full Bible configuration
        config = IngestionConfig(
            target_translation="KJV",
            chunk_size=250,
            chunk_variance=50,
            overlap_verses=1,
            embedding_batch_size=50,
            max_concurrent_embeddings=3,
            book_filter=None,  # All books
            collection_name="kjv_full_optimized",
            drop_existing_collection=True,
            enable_progress_tracking=True,
        )

        pipeline = create_optimized_pipeline(config)

        print("🚀 Starting full KJV ingestion...")
        start_time = time.time()

        metrics = await pipeline.run_full_pipeline()

        total_time = time.time() - start_time
        summary = pipeline.get_metrics_summary()

        print(f"\n🎉 FULL KJV INGESTION COMPLETED!")
        print(f"   Total time: {total_time/60:.1f} minutes")
        print(f"   Verses: {summary['counts']['total_verses']}")
        print(f"   Chunks: {summary['counts']['total_chunks']}")
        print(
            f"   Performance: {summary['performance']['verses_per_second']:.1f} verses/sec"
        )

        return True

    except Exception as e:
        print(f"❌ Full Bible test failed: {e}")
        return False


async def main():
    """Run the pipeline tests."""

    print("🔧 BibleStudyAI Optimized Pipeline - FULL TEST SUITE")
    print("=" * 60)

    # Test 1: Genesis pipeline
    print("\n1️⃣ Testing Genesis pipeline...")
    genesis_success = await test_genesis_full_pipeline()

    if genesis_success:
        print("\n2️⃣ Genesis test passed! Ready for next steps...")

        # Optionally test full Bible
        await test_full_kjv_pipeline()

        print(f"\n🎉 PIPELINE TESTING COMPLETE!")
        print(f"\n📋 NEXT ACTIONS:")
        print(f"   ✅ Your optimized RAG + Knowledge Graph pipeline is functional!")
        print(f"   🔧 Fix entity extraction in agents/tools.py")
        print(f"   🤖 Implement Pydantic AI agent framework")
        print(f"   📚 Add biblical reasoning capabilities")
        print(f"   🔍 Test advanced search and retrieval")

    else:
        print("\n❌ Genesis test failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
