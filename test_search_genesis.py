#!/usr/bin/env python3
"""
Quick test of the ingested Genesis data in Milvus.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root
project_root = Path(__file__).parent.absolute()

# Load environment variables from backend directory
env_file = project_root / "backend" / ".env"
load_dotenv(env_file)

# Override hosts for local testing
os.environ["MILVUS_HOST"] = "localhost"
os.environ["REDIS_URL"] = "redis://localhost:6379"

# Add backend to path
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from database.optimized_milvus import create_optimized_milvus_manager
from loguru import logger


async def test_search():
    """Test search on the ingested Genesis data."""

    logger.info("🔍 Testing search on ingested Genesis data...")

    # Create Milvus manager
    milvus_manager = create_optimized_milvus_manager(
        connection_alias="biblical_rag_search"
    )

    try:
        # Initialize connection
        await milvus_manager.initialize()

        # Check available collections
        logger.info("📋 Checking available collections...")
        # List collections (if method exists)
        try:
            from pymilvus import utility

            collections = utility.list_collections(
                using=milvus_manager.connection_alias
            )
            logger.info(f"Available collections: {collections}")
        except Exception as e:
            logger.warning(f"Could not list collections: {e}")

        # Use the test_genesis collection
        collection_name = "test_genesis"
        logger.info(f"Using collection: {collection_name}")

        # Test searches
        queries = [
            "In the beginning God created",
            "Adam and Eve",
            "Noah's ark and the flood",
            "Abraham and Isaac",
        ]

        for query in queries:
            logger.info(f"\n📖 Searching for: '{query}'")

            results = await milvus_manager.hybrid_search(
                collection_name=collection_name, query_text=query, limit=3
            )

            if results:
                logger.success(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"  {i}. Score: {result.get('score', 0):.3f}")
                    logger.info(f"     Book: {result.get('book', 'Unknown')}")
                    logger.info(
                        f"     Chapter: {result.get('chapter', 'Unknown')}:{result.get('verse', 'Unknown')}"
                    )
                    logger.info(f"     Text: {result.get('text', '')[:150]}...")
            else:
                logger.warning("No results found")

        logger.success("🎉 Search test completed!")

    except Exception as e:
        logger.error(f"❌ Search test failed: {e}")
        logger.exception("Full error details:")
    finally:
        # Cleanup
        await milvus_manager.close()


if __name__ == "__main__":
    asyncio.run(test_search())
