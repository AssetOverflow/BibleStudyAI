import asyncio
from typing import List
from loguru import logger
import pandas as pd
from tqdm import tqdm

# Adjust imports to be relative from the script's location if run as a module
from services.bible_service import BibleService
from data_ingestion.chunker import HybridChunker
from data_ingestion.embedder import Embedder
from data_ingestion.graph_builder import GraphBuilder
from database.milvus_vector import MilvusManager
from database.neo4j_graph import Neo4jManager
from utils.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    MILVUS_ALIAS,
    MILVUS_HOST,
    MILVUS_PORT,
)


class IngestionPipeline:
    """
    Orchestrates the entire data ingestion process from source to databases.
    """

    def __init__(self):
        logger.info("Initializing Ingestion Pipeline...")
        self.bible_service = BibleService(parquet_dir="db/bibles/parquet/")
        self.chunker = HybridChunker(
            target_chunk_size=200, size_variance=50, overlap_sentences=2
        )
        self.embedder = Embedder()
        self.graph_builder = GraphBuilder()

        # Initialize database managers
        self.milvus_manager = MilvusManager()
        self.neo4j_manager = Neo4jManager()

        self.collection_name = "bible_verses"
        logger.info("Ingestion Pipeline initialized.")

    async def run_ingestion(self):
        """
        Executes the full ingestion pipeline for all Bible translations.
        """
        logger.info("Starting data ingestion process...")

        # 1. Setup Databases
        self.setup_databases()

        # 2. Load Bible Data
        translations = self.bible_service.get_translations()
        if not translations:
            logger.error("No Bible translations found. Aborting ingestion.")
            return

        # Process each translation
        for translation in tqdm(translations, desc="Processing Translations"):
            logger.info(f"Processing translation: {translation}")

            # Get all books for this translation
            books = self.bible_service.get_books(translation)
            if not books:
                logger.warning(f"No books found for translation {translation}")
                continue

            for book in tqdm(books, desc=f"Books in {translation}", leave=False):
                # Get chapters for this book
                chapters = self.bible_service.get_chapters(translation, book)
                if not chapters:
                    continue

                for chapter in chapters:
                    # Get all verses for this chapter
                    verses = self.bible_service.get_verses(translation, book, chapter)
                    if not verses:
                        continue

                    # Combine verses into chapter text
                    chapter_text = " ".join([verse["text"] for verse in verses])

                    # 3. Chunk the text
                    chunks = self.chunker.chunk_text(chapter_text)

                    # 4. Generate Embeddings and Graph in parallel with batching
                    chunk_batch = []
                    chunk_metadata_batch = []

                    for i, chunk_text in enumerate(
                        tqdm(chunks, desc="Processing Chunks", leave=False)
                    ):
                        chunk_id = f"{translation}_{book}_{chapter}_{i}"
                        metadata = {
                            "translation": translation,
                            "book": book,
                            "chapter": chapter,
                            "chunk_index": i,
                        }

                        chunk_batch.append(chunk_text)
                        chunk_metadata_batch.append((chunk_id, metadata))

                        # Process in batches of 10 for better performance
                        if len(chunk_batch) >= 10 or i == len(chunks) - 1:
                            await self._process_chunk_batch(
                                chunk_batch, chunk_metadata_batch
                            )
                            chunk_batch = []
                            chunk_metadata_batch = []

        logger.info("Data ingestion process completed.")
        self.milvus_manager.flush(self.collection_name)
        self.neo4j_manager.close()
        logger.info("Database connections closed.")

    async def _process_chunk_batch(
        self, chunk_batch: List[str], metadata_batch: List[tuple]
    ):
        """
        Processes a batch of chunks efficiently with parallel embedding and graph generation.

        Args:
            chunk_batch: List of text chunks to process
            metadata_batch: List of (chunk_id, metadata) tuples
        """
        # Generate embeddings for the entire batch
        embeddings = []
        for chunk_text in chunk_batch:
            embedding = await self.embedder.embed_text(chunk_text)
            embeddings.append(embedding)

        # Generate graph data in parallel
        graph_tasks = [
            self.graph_builder.build_graph_from_text(chunk_text)
            for chunk_text in chunk_batch
        ]
        graph_results = await asyncio.gather(*graph_tasks, return_exceptions=True)

        # Process results and ingest into databases
        milvus_batch_data = []

        for i, (chunk_text, (chunk_id, metadata)) in enumerate(
            zip(chunk_batch, metadata_batch)
        ):
            # Handle embedding
            if i < len(embeddings) and embeddings[i] is not None:
                milvus_data = {
                    "id": chunk_id,
                    "vector": embeddings[i],
                    "text": chunk_text,
                    **metadata,
                }
                milvus_batch_data.append(milvus_data)
            else:
                logger.warning(f"Skipping chunk {chunk_id} due to embedding failure.")
                continue

            # Handle graph data
            if i < len(graph_results) and not isinstance(graph_results[i], Exception):
                graph_data = graph_results[i]
                if graph_data and graph_data.get("nodes") and graph_data.get("edges"):
                    try:
                        self.neo4j_manager.add_graph_from_json(graph_data)
                    except Exception as e:
                        logger.error(
                            f"Failed to add graph data for chunk {chunk_id}: {e}"
                        )

        # Batch insert into Milvus
        if milvus_batch_data:
            try:
                # Prepare data in the format expected by Milvus schema (excluding auto-generated id)
                translations = [item["translation"] for item in milvus_batch_data]
                books = [item["book"] for item in milvus_batch_data]
                chapters = [item["chapter"] for item in milvus_batch_data]
                chunk_indices = [item["chunk_index"] for item in milvus_batch_data]
                texts = [item["text"] for item in milvus_batch_data]
                vectors = [item["vector"] for item in milvus_batch_data]

                formatted_data = [
                    translations,
                    books,
                    chapters,
                    chunk_indices,
                    texts,
                    vectors,
                ]

                self.milvus_manager.insert_batch(
                    collection_name=self.collection_name, data=formatted_data
                )
                logger.debug(
                    f"Successfully ingested batch of {len(milvus_batch_data)} chunks"
                )
            except Exception as e:
                logger.error(f"Failed to ingest batch into Milvus: {e}")

    def setup_databases(self):
        """
        Ensures collections and indexes are created in Milvus and Neo4j.
        """
        logger.info("Setting up databases...")
        # Milvus setup
        if not self.milvus_manager.has_collection(self.collection_name):
            self.milvus_manager.create_collection(self.collection_name)
            self.milvus_manager.create_index(self.collection_name)

        # Neo4j setup (constraints for data integrity)
        try:
            self.neo4j_manager.create_uniqueness_constraint("Node", "id")
            self.neo4j_manager.create_uniqueness_constraint("Entity", "name")
        except Exception as e:
            logger.warning(f"Failed to create Neo4j constraints: {e}")
        logger.info("Databases setup complete.")


async def main():
    pipeline = IngestionPipeline()
    try:
        await pipeline.run_ingestion()
    except Exception as e:
        logger.opt(exception=True).critical(
            f"A critical error occurred during the ingestion pipeline: {e}"
        )
    finally:
        # Ensure connections are closed even if errors occur
        try:
            if pipeline.neo4j_manager:
                pipeline.neo4j_manager.close()
        except:
            pass
        logger.info("Pipeline execution finished.")


if __name__ == "__main__":
    # This allows the script to be run directly for initial data loading
    # Ensure you have a .env file or environment variables set for database connections
    logger.add("ingestion.log", rotation="500 MB")  # Add a log file
    asyncio.run(main())
