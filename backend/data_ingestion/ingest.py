import asyncio
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

                # 3. Chunk Text
                chunks = self.chunker.chunk(text)

                for i, chunk_text in enumerate(
                    tqdm(chunks, desc="Processing Chunks", leave=False)
                ):
                    chunk_id = f"{translation}_{book}_{chapter}_{i}"

                    # 4. Generate Embeddings and Graph
                    embedding_task = self.embedder.embed_text(chunk_text)
                    graph_task = self.graph_builder.build_graph_from_text(chunk_text)

                    embedding, graph_data = await asyncio.gather(
                        embedding_task, graph_task
                    )

                    if embedding is None:
                        logger.warning(
                            f"Skipping chunk {chunk_id} due to embedding failure."
                        )
                        continue

                    # 5. Ingest into Databases
                    # Ingest into Milvus
                    metadata = {
                        "translation": translation,
                        "book": book,
                        "chapter": chapter,
                        "chunk_index": i,
                    }
                    self.milvus_manager.insert_entity(
                        collection_name=self.collection_name,
                        data=[
                            {
                                "id": chunk_id,
                                "vector": embedding,
                                "text": chunk_text,
                                **metadata,
                            }
                        ],
                    )

                    # Ingest into Neo4j
                    if (
                        graph_data
                        and graph_data.get("nodes")
                        and graph_data.get("edges")
                    ):
                        self.neo4j_manager.add_graph_from_json(graph_data)

        logger.info("Data ingestion process completed.")
        self.milvus_manager.flush(self.collection_name)
        self.neo4j_manager.close()
        logger.info("Database connections closed.")

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
