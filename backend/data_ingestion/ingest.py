import asyncio
from typing import List
from loguru import logger
import pandas as pd
from tqdm import tqdm

# Adjust imports to be relative from the script's location if run as a module
from ..services.bible_service import BibleService
from .chunker import HybridChunker
from .embedder import Embedder
from .graph_builder import GraphBuilder
from ..database.milvus_vector import MilvusManager
from ..database.neo4j_graph import Neo4jManager
from ..utils.config import (
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
        self.bible_service = BibleService()
        self.chunker = HybridChunker(
            paragraph_separator="\n\n", max_words=200, overlap_sentences=2
        )
        self.embedder = Embedder()
        self.graph_builder = GraphBuilder()

        # Initialize database managers
        self.milvus_manager = MilvusManager()
        self.neo4j_manager = Neo4jManager(
            uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD
        )

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
        all_translations_df = self.bible_service.get_all_translations()
        if all_translations_df.empty:
            logger.error("No Bible data found. Aborting ingestion.")
            return

        # Using tqdm for progress tracking
        for translation, group in tqdm(
            all_translations_df.groupby("translation"), desc="Processing Translations"
        ):
            logger.info(f"Processing translation: {translation}")

            # Combine verses into chapters for meaningful chunking
            full_text = (
                group.sort_values(by=["book", "chapter", "verse"])
                .groupby(["book", "chapter"])["text"]
                .apply(" ".join)
                .reset_index()
            )

            for _, row in tqdm(
                full_text.iterrows(),
                total=full_text.shape[0],
                desc=f"Books/Chapters in {translation}",
                leave=False,
            ):
                book = row["book"]
                chapter = row["chapter"]
                text = row["text"]

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

    async def _process_chunk_batch(self, chunk_batch: List[str], metadata_batch: List[tuple]):
        """
        Processes a batch of chunks efficiently with parallel embedding and graph generation.
        
        Args:
            chunk_batch: List of text chunks to process
            metadata_batch: List of (chunk_id, metadata) tuples
        """
        # Generate embeddings for the entire batch
        embeddings = await self.embedder.get_embeddings(chunk_batch)
        
        # Generate graph data in parallel
        graph_tasks = [
            self.graph_builder.build_graph_from_text(chunk_text) 
            for chunk_text in chunk_batch
        ]
        graph_results = await asyncio.gather(*graph_tasks, return_exceptions=True)
        
        # Process results and ingest into databases
        milvus_batch_data = []
        
        for i, (chunk_text, (chunk_id, metadata)) in enumerate(zip(chunk_batch, metadata_batch)):
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
                if (
                    graph_data
                    and graph_data.get("nodes")
                    and graph_data.get("edges")
                ):
                    try:
                        self.neo4j_manager.add_graph_from_json(graph_data)
                    except Exception as e:
                        logger.error(f"Failed to add graph data for chunk {chunk_id}: {e}")
        
        # Batch insert into Milvus
        if milvus_batch_data:
            try:
                self.milvus_manager.insert_entity(
                    collection_name=self.collection_name,
                    data=milvus_batch_data
                )
                logger.debug(f"Successfully ingested batch of {len(milvus_batch_data)} chunks")
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
        self.neo4j_manager.create_uniqueness_constraint("Node", "id")
        self.neo4j_manager.create_uniqueness_constraint("Entity", "name")
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
        if pipeline.neo4j_manager.driver:
            pipeline.neo4j_manager.close()
        logger.info("Pipeline execution finished.")


if __name__ == "__main__":
    # This allows the script to be run directly for initial data loading
    # Ensure you have a .env file or environment variables set for database connections
    logger.add("ingestion.log", rotation="500 MB")  # Add a log file
    asyncio.run(main())
