from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, utility
from loguru import logger

from ..services.ai_integration import ai_integration_client
from ..services.bible_service import BibleService
from ..database.milvus_vector import get_milvus_connection

COLLECTION_NAME = "bible_verses"
DIMENSION = 768  # Example dimension for sentence-transformers/all-MiniLM-L6-v2


def create_milvus_collection():
    """Creates the Milvus collection for storing Bible verse embeddings."""
    conn = get_milvus_connection()
    if conn is None:
        logger.error("Cannot create Milvus collection, no connection.")
        return

    if utility.has_collection(COLLECTION_NAME):
        logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        FieldSchema(name="translation", dtype=DataType.VARCHAR, max_length=16),
        FieldSchema(name="book", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="chapter", dtype=DataType.INT64),
        FieldSchema(name="verse", dtype=DataType.INT64),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields, description="Bible verse embeddings")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    logger.info(f"Creating index for collection '{COLLECTION_NAME}'...")
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    logger.success(f"Index for '{COLLECTION_NAME}' created successfully.")


async def ingest_bible_verses_to_milvus():
    """Ingests Bible verses and their embeddings into Milvus."""
    create_milvus_collection()

    bible_service = BibleService(parquet_dir="KoinoniaHouse/db/bibles/parquet/")
    collection = Collection(COLLECTION_NAME)

    for translation in bible_service.get_translations():
        logger.info(f"Ingesting verses for translation: {translation}")
        df = bible_service.bibles[translation]

        # Check for existing data to avoid duplicates (simple check)
        # A more robust check might involve checking specific verse IDs
        res = collection.query(expr=f'translation == "{translation}"', limit=1)
        if res:
            logger.info(
                f"Translation '{translation}' already has data in Milvus. Skipping."
            )
            continue

        texts = df["text"].tolist()
        embeddings = await ai_integration_client.get_embedding(texts)

        if not embeddings:
            logger.error(f"Could not generate embeddings for {translation}. Skipping.")
            continue

        data = [
            embeddings,
            [translation] * len(df),
            df["book"].tolist(),
            df["chapter"].tolist(),
            df["verse"].tolist(),
            texts,
        ]

        collection.insert(data)
        logger.success(f"Successfully inserted {len(df)} verses for {translation}.")

    collection.flush()
    logger.info("Milvus data ingestion complete and flushed.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(ingest_bible_verses_to_milvus())
