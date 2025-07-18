"""
Handles database connections and operations for Milvus.
"""

import os
from pymilvus import connections, utility
from loguru import logger

from utils.config import settings


def get_milvus_connection():
    """
    Milvus connection dependency injector.
    """
    alias = "default"
    try:
        # Check if connection already exists
        existing_connections = connections.list_connections()
        if alias not in existing_connections:
            logger.info(
                f"Connecting to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
            )
            connections.connect(
                alias=alias, host=settings.MILVUS_HOST, port=settings.MILVUS_PORT
            )
            logger.success("Successfully connected to Milvus.")
        # Return the alias instead of trying to get the connection object
        return alias
    except Exception as e:
        logger.opt(exception=True).error(f"Failed to connect to Milvus: {e}")
        return None


def close_milvus_connection():
    """
    Closes the Milvus connection.
    """
    alias = "default"
    if utility.has_connection(alias):
        try:
            connections.disconnect(alias)
            logger.info("Milvus connection closed.")
        except Exception as e:
            logger.error(f"Failed to close Milvus connection: {e}")


class MilvusManager:
    def __init__(self):
        self.connection_alias = get_milvus_connection()
        self.is_connected = self.connection_alias is not None

    def is_available(self):
        """Check if Milvus connection is available."""
        return self.is_connected and self.connection_alias is not None

    def has_collection(self, collection_name: str) -> bool:
        """Check if a collection exists in Milvus."""
        if not self.is_available():
            logger.warning("Milvus connection not available for collection check")
            return False

        try:
            return utility.has_collection(collection_name, using=self.connection_alias)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def create_collection(self, collection_name: str):
        """Create a new collection in Milvus for Bible verses."""
        if not self.is_available():
            logger.warning("Milvus connection not available for collection creation")
            return False

        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema

            # Define schema for Bible verses
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="translation", dtype=DataType.VARCHAR, max_length=10),
                FieldSchema(name="book", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="chapter", dtype=DataType.INT64),
                FieldSchema(name="chunk_index", dtype=DataType.INT64),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),  # OpenAI text-embedding-3-small dimension
            ]

            schema = CollectionSchema(fields, f"Collection for {collection_name}")
            collection = Collection(collection_name, schema, using=self.connection_alias)
            
            logger.success(f"Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False

    def create_index(self, collection_name: str):
        """Create an index on the embedding field for efficient vector search."""
        if not self.is_available():
            logger.warning("Milvus connection not available for index creation")
            return False

        try:
            from pymilvus import Collection

            collection = Collection(collection_name, using=self.connection_alias)
            
            # Create index for vector search
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            collection.create_index("embedding", index_params)
            logger.success(f"Created index for collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating index for {collection_name}: {e}")
            return False

    def insert_entity(self, collection_name: str, entity_data: dict):
        """Insert a single entity into the collection."""
        if not self.is_available():
            logger.warning("Milvus connection not available for insertion")
            return False

        try:
            from pymilvus import Collection

            collection = Collection(collection_name, using=self.connection_alias)
            
            # Convert single entity to list format expected by Milvus
            data = [
                [entity_data["translation"]],
                [entity_data["book"]],
                [entity_data["chapter"]],
                [entity_data["verse"]],
                [entity_data["text"]],
                [entity_data["embedding"]]
            ]
            
            collection.insert(data)
            return True

        except Exception as e:
            logger.error(f"Error inserting entity into {collection_name}: {e}")
            return False

    def insert_batch(self, collection_name: str, data: list):
        """Insert a batch of entities into the collection."""
        if not self.is_available():
            logger.warning("Milvus connection not available for batch insertion")
            return False

        try:
            from pymilvus import Collection

            collection = Collection(collection_name, using=self.connection_alias)
            collection.insert(data)
            logger.info(f"Successfully inserted batch of {len(data[0]) if data else 0} entities into {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error inserting batch into {collection_name}: {e}")
            return False

    def flush(self, collection_name: str):
        """Flush data to storage."""
        if not self.is_available():
            logger.warning("Milvus connection not available for flush")
            return False

        try:
            from pymilvus import Collection

            collection = Collection(collection_name, using=self.connection_alias)
            collection.flush()
            logger.info(f"Flushed data for collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error flushing collection {collection_name}: {e}")
            return False

    def search(self, collection_name: str, query_vectors, top_k: int = 5):
        """
        Perform a vector search in Milvus.

        Args:
            collection_name (str): Name of the collection to search
            query_vectors: List of query vectors
            top_k (int): Number of top results to return

        Returns:
            Search results from Milvus
        """
        if not self.is_available():
            logger.warning("Milvus connection not available for search")
            return []

        try:
            from pymilvus import Collection

            collection = Collection(collection_name, using=self.connection_alias)

            # Perform the search
            search_results = collection.search(
                data=query_vectors,
                anns_field="embedding",  # Assuming the vector field is named "embedding"
                param={"metric_type": "COSINE", "params": {"nprobe": 16}},
                limit=top_k,
                output_fields=["*"],  # Return all fields
            )

            return search_results

        except Exception as e:
            logger.error(f"Error during Milvus search: {e}")
            return []

    def close(self):
        close_milvus_connection()
