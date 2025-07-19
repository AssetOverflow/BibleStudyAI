#!/usr/bin/env python3
"""
Genesis ingestion test with full optimized pipeline.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

from data_ingestion.optimized_pipeline import create_optimized_pipeline, IngestionConfig
from loguru import logger


async def test_genesis_full_pipeline():
    """Test the complete optimized pipeline with Genesis."""

    logger.info("🚀 Starting Genesis ingestion with optimized pipeline...")

    # Configure for Genesis book
    config = IngestionConfig(
        target_translation="KJV",
        chunk_size=200,
        chunk_variance=40,
        overlap_verses=1,
        embedding_batch_size=20,
        max_concurrent_embeddings=3,
        book_filter=["Genesis"],  # Start with Genesis
        collection_name="genesis_optimized_test",
        drop_existing_collection=True,
        enable_progress_tracking=True,
        enable_chunking=True,
        enable_embedding=True,
        enable_vector_storage=True,
        enable_graph_building=False,  # Disable for now until entity extraction is fixed
    )

    # Create pipeline
    pipeline = create_optimized_pipeline(config)

    try:
        logger.info("Initializing optimized pipeline components...")

        # Run the full pipeline
        metrics = await pipeline.run_full_pipeline()

        # Get comprehensive summary
        summary = pipeline.get_metrics_summary()

        # Print detailed results
        print("\n" + "=" * 80)
        print("🎉 GENESIS OPTIMIZED INGESTION COMPLETED!")
        print("=" * 80)

        print(f"\n📖 BIBLE DATA PROCESSED:")
        print(f"   Translation: {summary['configuration']['translation']}")
        print(f"   Books: {summary['configuration']['book_filter']}")
        print(f"   Chunk size target: {summary['configuration']['chunk_size']} words")
        print(
            f"   Embedding batch size: {summary['configuration']['embedding_batch_size']}"
        )

        print(f"\n📊 PROCESSING RESULTS:")
        print(f"   Total verses: {summary['counts']['total_verses']:,}")
        print(f"   Chunks created: {summary['counts']['total_chunks']:,}")
        print(
            f"   Successful embeddings: {summary['counts']['successful_embeddings']:,}"
        )
        print(f"   Failed embeddings: {summary['counts']['failed_embeddings']:,}")

        # Calculate success rates
        if summary["counts"]["total_chunks"] > 0:
            success_rate = (
                summary["counts"]["successful_embeddings"]
                / summary["counts"]["total_chunks"]
            )
            print(f"   Success rate: {success_rate:.1%}")

        print(f"\n⏱️  PERFORMANCE TIMING:")
        print(f"   Total time: {summary['timing']['total_time']:.2f}s")
        print(f"   Chunking: {summary['timing']['chunking_time']:.2f}s")
        print(f"   Embedding: {summary['timing']['embedding_time']:.2f}s")
        print(f"   Vector storage: {summary['timing']['vector_storage_time']:.2f}s")
        print(f"   Graph building: {summary['timing']['graph_building_time']:.2f}s")

        print(f"\n🚀 THROUGHPUT METRICS:")
        print(f"   Verses/second: {summary['performance']['verses_per_second']:.1f}")
        print(f"   Chunks/second: {summary['performance']['chunks_per_second']:.1f}")
        print(
            f"   Embeddings/second: {summary['performance']['embeddings_per_second']:.1f}"
        )

        # Performance assessment
        total_time = summary["timing"]["total_time"]
        chunks_per_sec = summary["performance"]["chunks_per_second"]

        print(f"\n📈 PERFORMANCE ASSESSMENT:")
        if chunks_per_sec > 10:
            print("   🔥 EXCELLENT: Very high throughput!")
        elif chunks_per_sec > 5:
            print("   ✅ GOOD: Solid performance")
        elif chunks_per_sec > 2:
            print("   👍 FAIR: Acceptable performance")
        else:
            print("   ⚠️  SLOW: Consider optimization")

        print(f"\n🗄️  STORAGE STATUS:")
        print(f"   Milvus collection: {config.collection_name}")
        print(f"   Vector storage enabled: ✅")
        print(f"   Knowledge graph: ⏸️  (Disabled for this test)")

        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Test vector search on stored chunks")
        print(f"   2. Fix entity extraction in agents/tools.py")
        print(f"   3. Enable knowledge graph building")
        print(f"   4. Scale to full KJV Bible")

        return True

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_vector_search():
    """Test the vector search on ingested data."""

    logger.info("🔍 Testing vector search on ingested Genesis data...")

    try:
        from database.optimized_milvus import create_optimized_milvus_manager
        from data_ingestion.optimized_embedder import (
            create_optimized_embedder,
            EmbeddingConfig,
        )

        # Initialize components
        milvus_manager = create_optimized_milvus_manager()
        await milvus_manager.initialize()

        embedder_config = EmbeddingConfig(enable_caching=True)
        embedder = create_optimized_embedder(embedder_config)
        await embedder.initialize()

        # Test queries
        test_queries = [
            "In the beginning God created",
            "Let there be light",
            "Adam and Eve in the garden",
            "Noah and the flood",
        ]

        collection_name = "genesis_optimized_test"

        print(f"\n🔍 VECTOR SEARCH TEST RESULTS:")
        print(f"Collection: {collection_name}")

        for query in test_queries:
            # Generate query embedding
            query_embedding = await embedder.embed_single_text(query)

            if query_embedding:
                # Search for similar chunks
                results = await milvus_manager.hybrid_search(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    query_text=query,
                    limit=3,
                )

                print(f"\n   Query: '{query}'")
                print(f"   Results: {len(results)}")

                for i, result in enumerate(results[:2]):  # Show top 2
                    score = result.get("score", 0.0)
                    reference = f"{result.get('book', 'Unknown')} {result.get('chapter', '?')}:{result.get('start_verse', '?')}-{result.get('end_verse', '?')}"
                    content = result.get("content", "")[:100] + "..."

                    print(f"     {i+1}. {reference} (score: {score:.3f})")
                    print(f"        {content}")
            else:
                print(f"   Query: '{query}' - Failed to generate embedding")

        # Get collection stats
        stats = await milvus_manager.get_collection_stats(collection_name)
        print(f"\n📊 COLLECTION STATISTICS:")
        print(f"   Total entities: {stats.get('num_entities', 0):,}")
        print(f"   Has index: {stats.get('has_index', False)}")
        print(f"   Indexes: {stats.get('indexes', [])}")

        await milvus_manager.close()
        await embedder.close()

        print(f"\n✅ Vector search test completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Vector search test failed: {e}")
        return False


async def main():
    """Run the complete Genesis test suite."""

    print("🚀 BibleStudyAI Optimized Pipeline - Genesis Test")
    print("=" * 60)

    # Check environment
    required_vars = ["OPENAI_API_KEY", "MILVUS_HOST", "REDIS_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("   Make sure .env file is properly loaded")
        return

    print("✅ Environment variables loaded")
    print(f"   OpenAI API: {'*' * 20}{os.getenv('OPENAI_API_KEY', '')[-10:]}")
    print(f"   Milvus host: {os.getenv('MILVUS_HOST')}")
    print(f"   Redis URL: {os.getenv('REDIS_URL', '').split('@')[0]}@***")

    # Test 1: Full pipeline ingestion
    print(f"\n1️⃣ Running Genesis ingestion pipeline...")
    ingestion_success = await test_genesis_full_pipeline()

    if not ingestion_success:
        print(f"\n❌ Ingestion failed - stopping tests")
        return

    # Test 2: Vector search
    print(f"\n2️⃣ Testing vector search capabilities...")
    search_success = await test_vector_search()

    # Final summary
    print(f"\n" + "=" * 60)
    if ingestion_success and search_success:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Your optimized agentic RAG system is working!")
        print("\n🎯 Ready for next phase:")
        print("   • Fix entity extraction in agents/tools.py")
        print("   • Implement Pydantic AI agent framework")
        print("   • Enable knowledge graph building")
        print("   • Scale to full Bible ingestion")
    else:
        print("❌ Some tests failed - check logs above")


if __name__ == "__main__":
    asyncio.run(main())
