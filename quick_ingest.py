#!/usr/bin/env python3
"""
Quick Bible Ingestion Script for RAG Testing
Populates Milvus vector database with sample Bible verses for RAG functionality.
"""

import sys
import os
import asyncio
import pandas as pd
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.bible_service import BibleService
from data_ingestion.embedder import Embedder
from database.milvus_vector import MilvusManager
from loguru import logger


async def quick_bible_ingestion():
    """Quick ingestion of sample Bible verses for testing RAG"""

    logger.info("🚀 Starting Quick Bible Ingestion for RAG Testing...")

    # Initialize components
    bible_service = BibleService(parquet_dir="db/bibles/parquet/")
    embedder = Embedder()
    milvus_manager = MilvusManager()

    collection_name = "bible_verses"

    # Check if collection exists, if not create it
    try:
        if not milvus_manager.has_collection(collection_name):
            logger.info(f"Creating collection: {collection_name}")
            milvus_manager.create_collection(collection_name)
            milvus_manager.create_index(collection_name)
        else:
            logger.info(f"Collection {collection_name} already exists")

        # Get sample data from KJV - just a few well-known verses for testing
        sample_verses = [
            {"book": "John", "chapter": 3, "verse": 16, "translation": "KJV"},
            {"book": "Psalms", "chapter": 23, "verse": 1, "translation": "KJV"},
            {"book": "Romans", "chapter": 8, "verse": 28, "translation": "KJV"},
            {"book": "1 Corinthians", "chapter": 13, "verse": 4, "translation": "KJV"},
            {"book": "1 Corinthians", "chapter": 13, "verse": 5, "translation": "KJV"},
            {"book": "1 Corinthians", "chapter": 13, "verse": 6, "translation": "KJV"},
            {"book": "1 Corinthians", "chapter": 13, "verse": 7, "translation": "KJV"},
            {"book": "1 Corinthians", "chapter": 13, "verse": 8, "translation": "KJV"},
            {"book": "Matthew", "chapter": 5, "verse": 3, "translation": "KJV"},
            {"book": "Matthew", "chapter": 5, "verse": 4, "translation": "KJV"},
            {"book": "Ephesians", "chapter": 2, "verse": 8, "translation": "KJV"},
            {"book": "Ephesians", "chapter": 2, "verse": 9, "translation": "KJV"},
            {"book": "Philippians", "chapter": 4, "verse": 13, "translation": "KJV"},
            {"book": "Hebrews", "chapter": 11, "verse": 1, "translation": "KJV"},
            {"book": "James", "chapter": 2, "verse": 17, "translation": "KJV"},
        ]

        # Get actual verse text from Bible service
        verses_to_ingest = []
        for verse_ref in sample_verses:
            try:
                verses = bible_service.get_verses(
                    verse_ref["translation"], verse_ref["book"], verse_ref["chapter"]
                )
                if verses:
                    target_verse = next(
                        (v for v in verses if v["verse"] == verse_ref["verse"]), None
                    )
                    if target_verse:
                        verses_to_ingest.append(target_verse)
                        logger.debug(
                            f"Added {verse_ref['book']} {verse_ref['chapter']}:{verse_ref['verse']}"
                        )
            except Exception as e:
                logger.warning(f"Could not get verse {verse_ref}: {e}")

        logger.info(f"📖 Collected {len(verses_to_ingest)} verses for ingestion")

        # Process verses and create embeddings
        ingestion_data = []
        for i, verse in enumerate(verses_to_ingest):
            try:
                # Create verse text for embedding
                verse_text = f"{verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text']}"

                # Generate embedding
                embedding = await embedder.embed_text(verse_text)
                if embedding:
                    # Prepare data for Milvus
                    data_point = {
                        "id": f"verse_{i}",
                        "vector": embedding,
                        "text": verse_text,
                        "translation": "KJV",
                        "book": verse["book"],
                        "chapter": verse["chapter"],
                        "verse": verse["verse"],
                    }
                    ingestion_data.append(data_point)
                    logger.debug(
                        f"✅ Embedded: {verse['book']} {verse['chapter']}:{verse['verse']}"
                    )
                else:
                    logger.warning(
                        f"❌ Failed to embed: {verse['book']} {verse['chapter']}:{verse['verse']}"
                    )

            except Exception as e:
                logger.error(f"Error processing verse {verse}: {e}")

        # Insert into Milvus
        if ingestion_data:
            logger.info(f"📊 Inserting {len(ingestion_data)} verses into Milvus...")

            # Prepare data in the format Milvus expects
            ids = [item["id"] for item in ingestion_data]
            vectors = [item["vector"] for item in ingestion_data]
            texts = [item["text"] for item in ingestion_data]
            translations = [item["translation"] for item in ingestion_data]
            books = [item["book"] for item in ingestion_data]
            chapters = [item["chapter"] for item in ingestion_data]
            verses = [item["verse"] for item in ingestion_data]

            milvus_data = [ids, vectors, texts, translations, books, chapters, verses]

            try:
                milvus_manager.insert_entity(collection_name, milvus_data)
                logger.success(
                    f"✅ Successfully ingested {len(ingestion_data)} verses!"
                )

                # Test search
                test_query = "love"
                logger.info(f"🔍 Testing search with query: '{test_query}'")
                test_embedding = await embedder.embed_text(test_query)
                if test_embedding:
                    search_results = milvus_manager.search(
                        collection_name=collection_name,
                        query_vectors=[test_embedding],
                        top_k=3,
                    )
                    if search_results and search_results[0]:
                        logger.success(
                            f"🎉 Search test successful! Found {len(search_results[0])} results"
                        )
                        for hit in search_results[0]:
                            logger.info(
                                f"   - {hit.entity.get('text', 'No text')[:100]}..."
                            )
                    else:
                        logger.warning("🤔 Search test returned no results")
                else:
                    logger.error("❌ Could not generate test embedding")

            except Exception as e:
                logger.error(f"❌ Failed to insert data into Milvus: {e}")
        else:
            logger.warning("⚠️ No data to ingest!")

    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise


async def main():
    """Main function"""
    logger.add("quick_ingestion.log", rotation="10 MB")

    try:
        await quick_bible_ingestion()
        logger.success("🎉 Quick Bible ingestion completed successfully!")
        print("\n✅ Bible verses have been ingested into Milvus vector database.")
        print("🤖 RAG system should now return meaningful responses!")

    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        print(f"\n❌ Ingestion failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
