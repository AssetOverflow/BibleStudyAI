"""
Optimized Milvus vector database manager for BibleStudyAI agentic RAG system.

Features:
- Async operations with connection pooling
- Rich metadata storage optimized for biblical content
- Hybrid search capabilities (vector + keyword)
- Batch operations with progress tracking
- Advanced indexing strategies
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import asdict
import json
from datetime import datetime
from loguru import logger

from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    Index,
)
from pymilvus.exceptions import MilvusException

from data_ingestion.chunker import BiblicalChunk
from utils.config import settings


class OptimizedMilvusManager:
    """
    Advanced Milvus manager optimized for biblical content and agentic RAG.
    """

    def __init__(self, connection_alias: str = "biblical_rag"):
        """
        Initialize the optimized Milvus manager.

        Args:
            connection_alias: Unique alias for this connection
        """
        self.connection_alias = connection_alias
        self.is_connected = False
        self._collections: Dict[str, Collection] = {}
        self._connection_lock = asyncio.Lock()

        # Biblical-specific schema configuration
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small
        self.max_text_length = 8000  # Increased for biblical passages
        self.max_metadata_length = 4000

        logger.info(
            f"Initialized OptimizedMilvusManager with alias: {connection_alias}"
        )

    async def initialize(self) -> bool:
        """Initialize connection to Milvus."""
        async with self._connection_lock:
            if self.is_connected:
                return True

            try:
                # Check if connection already exists
                existing_connections = connections.list_connections()

                if self.connection_alias not in existing_connections:
                    logger.info(
                        f"Connecting to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
                    )
                    connections.connect(
                        alias=self.connection_alias,
                        host=settings.MILVUS_HOST,
                        port=settings.MILVUS_PORT,
                        timeout=30,
                    )

                self.is_connected = True
                logger.success(
                    f"Successfully connected to Milvus with alias: {self.connection_alias}"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to connect to Milvus: {e}")
                self.is_connected = False
                return False

    async def close(self):
        """Close Milvus connection."""
        async with self._connection_lock:
            if self.is_connected:
                try:
                    # Collections don't need explicit closing in Milvus
                    # Just clear the cache
                    self._collections.clear()

                    # Disconnect
                    try:
                        connections.disconnect(self.connection_alias)
                    except Exception:
                        # Connection might already be closed
                        pass

                    self.is_connected = False
                    logger.info("Milvus connection closed")

                except Exception as e:
                    logger.error(f"Error closing Milvus connection: {e}")

    def _create_biblical_schema(self, collection_name: str) -> CollectionSchema:
        """
        Create optimized schema for biblical content.

        Args:
            collection_name: Name of the collection

        Returns:
            CollectionSchema for biblical data
        """

        fields = [
            # Primary key
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=64,
                description="Unique chunk identifier",
            ),
            # Core content fields
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=self.max_text_length,
                description="Biblical text content",
            ),
            # Biblical reference fields
            FieldSchema(
                name="translation",
                dtype=DataType.VARCHAR,
                max_length=20,
                description="Bible translation (KJV, ESV, etc.)",
            ),
            FieldSchema(
                name="book",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Bible book name",
            ),
            FieldSchema(
                name="chapter", dtype=DataType.INT64, description="Chapter number"
            ),
            FieldSchema(
                name="start_verse",
                dtype=DataType.INT64,
                description="Starting verse number",
            ),
            FieldSchema(
                name="end_verse",
                dtype=DataType.INT64,
                description="Ending verse number",
            ),
            # Chunk metadata
            FieldSchema(
                name="chunk_index",
                dtype=DataType.INT64,
                description="Index of chunk in document",
            ),
            FieldSchema(
                name="word_count",
                dtype=DataType.INT64,
                description="Number of words in chunk",
            ),
            FieldSchema(
                name="char_count",
                dtype=DataType.INT64,
                description="Number of characters in chunk",
            ),
            # Testament classification
            FieldSchema(
                name="testament",
                dtype=DataType.VARCHAR,
                max_length=10,
                description="Old or New Testament",
            ),
            # Literary classification
            FieldSchema(
                name="genre",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Literary genre (narrative, poetry, etc.)",
            ),
            FieldSchema(
                name="section_type",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="Section type (prophecy, law, etc.)",
            ),
            # Theological metadata
            FieldSchema(
                name="themes",
                dtype=DataType.VARCHAR,
                max_length=500,
                description="JSON list of theological themes",
            ),
            # Extended metadata
            FieldSchema(
                name="metadata_json",
                dtype=DataType.VARCHAR,
                max_length=self.max_metadata_length,
                description="Additional metadata as JSON",
            ),
            # Timestamps
            FieldSchema(
                name="created_at",
                dtype=DataType.VARCHAR,
                max_length=30,
                description="Creation timestamp",
            ),
            # Vector field
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.embedding_dim,
                description="Text embedding vector",
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description=f"Optimized biblical content collection: {collection_name}",
            enable_dynamic_field=True,  # Allow additional fields
        )

        return schema

    async def create_collection(
        self, collection_name: str, drop_if_exists: bool = False
    ) -> bool:
        """
        Create a new collection with biblical schema.

        Args:
            collection_name: Name of the collection
            drop_if_exists: Whether to drop existing collection

        Returns:
            True if successful, False otherwise
        """

        if not self.is_connected:
            await self.initialize()

        try:
            # Check if collection exists
            if utility.has_collection(collection_name, using=self.connection_alias):
                if drop_if_exists:
                    logger.warning(f"Dropping existing collection: {collection_name}")
                    utility.drop_collection(
                        collection_name, using=self.connection_alias
                    )
                else:
                    logger.info(f"Collection {collection_name} already exists")
                    return True

            # Create schema
            schema = self._create_biblical_schema(collection_name)

            # Create collection
            collection = Collection(
                name=collection_name, schema=schema, using=self.connection_alias
            )

            # Cache collection
            self._collections[collection_name] = collection

            logger.success(f"Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    async def create_optimized_index(self, collection_name: str) -> bool:
        """
        Create optimized indexes for biblical search.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful, False otherwise
        """

        try:
            collection = await self._get_collection(collection_name)

            # Vector index for semantic search
            vector_index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",  # Better for accuracy
                "params": {
                    "M": 16,  # Higher connectivity for better recall
                    "efConstruction": 200,  # Higher for better quality
                },
            }

            # Create vector index
            collection.create_index(
                field_name="embedding",
                index_params=vector_index_params,
                index_name="embedding_hnsw_idx",
            )

            # Scalar indexes for filtering
            scalar_indexes = [
                ("translation", {}),
                ("book", {}),
                ("chapter", {}),
                ("testament", {}),
                ("genre", {}),
                ("section_type", {}),
            ]

            for field_name, params in scalar_indexes:
                try:
                    collection.create_index(
                        field_name=field_name,
                        index_params=params,
                        index_name=f"{field_name}_idx",
                    )
                except Exception as e:
                    logger.warning(f"Failed to create index on {field_name}: {e}")

            logger.success(
                f"Created optimized indexes for collection: {collection_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create indexes for {collection_name}: {e}")
            return False

    async def _get_collection(self, collection_name: str) -> Collection:
        """Get collection instance with caching."""

        if collection_name not in self._collections:
            if not utility.has_collection(collection_name, using=self.connection_alias):
                raise ValueError(f"Collection {collection_name} does not exist")

            collection = Collection(collection_name, using=self.connection_alias)
            self._collections[collection_name] = collection

        return self._collections[collection_name]

    def _prepare_chunk_data(self, chunk: BiblicalChunk) -> Dict[str, Any]:
        """
        Prepare BiblicalChunk for Milvus insertion.

        Args:
            chunk: BiblicalChunk instance

        Returns:
            Dictionary with Milvus-compatible data
        """

        # Extract context from metadata
        context = chunk.metadata.get("context", {})

        # Prepare themes as JSON string
        themes_json = json.dumps(context.get("theological_themes", []))

        # Clean metadata for storage
        storage_metadata = {
            k: v for k, v in chunk.metadata.items() if k not in ["context"]
        }  # Remove large nested objects
        metadata_json = json.dumps(storage_metadata)

        # Truncate if too long
        if len(metadata_json) > self.max_metadata_length:
            metadata_json = metadata_json[: self.max_metadata_length - 3] + "..."

        data = {
            "id": chunk.id,
            "content": chunk.content[: self.max_text_length],
            "translation": chunk.translation,
            "book": chunk.book,
            "chapter": chunk.chapter,
            "start_verse": chunk.start_verse,
            "end_verse": chunk.end_verse,
            "chunk_index": chunk.chunk_index,
            "word_count": chunk.word_count,
            "char_count": chunk.char_count,
            "testament": chunk.metadata.get("testament", "unknown"),
            "genre": context.get("literary_genre", "general"),
            "section_type": context.get("section_type", "other"),
            "themes": themes_json,
            "metadata_json": metadata_json,
            "created_at": chunk.created_at.isoformat(),
            "embedding": chunk.embedding or [0.0] * self.embedding_dim,
        }

        return data

    async def insert_chunks_batch(
        self, collection_name: str, chunks: List[BiblicalChunk], batch_size: int = 100
    ) -> bool:
        """
        Insert chunks in optimized batches.

        Args:
            collection_name: Name of the collection
            chunks: List of BiblicalChunk objects
            batch_size: Number of chunks per batch

        Returns:
            True if successful, False otherwise
        """

        if not chunks:
            logger.warning("No chunks to insert")
            return True

        try:
            collection = await self._get_collection(collection_name)

            # Process in batches
            total_inserted = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]

                # Prepare batch data
                batch_data = []
                for chunk in batch:
                    if not chunk.embedding:
                        logger.warning(f"Chunk {chunk.id} has no embedding, skipping")
                        continue
                    batch_data.append(self._prepare_chunk_data(chunk))

                if not batch_data:
                    continue

                # Convert to columnar format for Milvus
                columnar_data = self._convert_to_columnar(batch_data)

                # Insert batch
                result = collection.insert(columnar_data)

                total_inserted += len(batch_data)
                logger.info(
                    f"Inserted batch {i//batch_size + 1}: {len(batch_data)} chunks "
                    f"(Total: {total_inserted}/{len(chunks)})"
                )

                # Small delay to prevent overwhelming Milvus
                await asyncio.sleep(0.1)

            # Flush to ensure data is persisted
            collection.flush()

            logger.success(
                f"Successfully inserted {total_inserted} chunks into {collection_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert chunks batch: {e}")
            return False

    def _convert_to_columnar(self, data_list: List[Dict[str, Any]]) -> List[List[Any]]:
        """Convert list of dictionaries to columnar format for Milvus."""

        if not data_list:
            return []

        # Get field names from schema order
        field_names = [
            "id",
            "content",
            "translation",
            "book",
            "chapter",
            "start_verse",
            "end_verse",
            "chunk_index",
            "word_count",
            "char_count",
            "testament",
            "genre",
            "section_type",
            "themes",
            "metadata_json",
            "created_at",
            "embedding",
        ]

        # Convert to columnar format
        columnar_data = []
        for field_name in field_names:
            column = [item[field_name] for item in data_list]
            columnar_data.append(column)

        return columnar_data

    async def hybrid_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        query_text: str = "",
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and metadata filtering.

        Args:
            collection_name: Name of the collection
            query_embedding: Query vector
            query_text: Original query text for keyword matching
            limit: Number of results to return
            filter_conditions: Additional filter conditions
            output_fields: Fields to return (None = all fields)

        Returns:
            List of search results
        """

        try:
            collection = await self._get_collection(collection_name)

            # Load collection if not loaded
            try:
                # Just try to load the collection, skip index checking
                # Index validation during creation is sufficient
                collection.load()
            except Exception as e:
                logger.warning(f"Could not load collection {collection_name}: {e}")
                # Try to continue anyway
                pass

            # Build filter expression
            filter_expr = self._build_filter_expression(filter_conditions)

            # Default output fields if not specified
            if output_fields is None:
                output_fields = [
                    "id",
                    "content",
                    "translation",
                    "book",
                    "chapter",
                    "start_verse",
                    "end_verse",
                    "word_count",
                    "testament",
                    "genre",
                    "section_type",
                    "themes",
                    "metadata_json",
                ]

            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64},  # Higher for better recall
            }

            # Perform vector search
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit * 2,  # Get more for re-ranking
                expr=filter_expr,
                output_fields=output_fields,
            )

            # Process results
            processed_results = []

            for hits in results:
                for hit in hits:
                    result = {
                        "id": hit.entity.get("id"),
                        "score": float(hit.score),
                        "distance": float(hit.distance),
                        **{field: hit.entity.get(field) for field in output_fields},
                    }

                    # Add keyword matching score if query text provided
                    if query_text:
                        content = result.get("content", "")
                        keyword_score = self._calculate_keyword_score(
                            query_text, content
                        )
                        result["keyword_score"] = keyword_score
                        result["combined_score"] = 0.7 * hit.score + 0.3 * keyword_score
                    else:
                        result["combined_score"] = hit.score

                    processed_results.append(result)

            # Sort by combined score if keyword matching was used
            if query_text:
                processed_results.sort(key=lambda x: x["combined_score"], reverse=True)

            return processed_results[:limit]

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    def _build_filter_expression(
        self, filter_conditions: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Build Milvus filter expression from conditions."""

        if not filter_conditions:
            return None

        expressions = []

        for field, value in filter_conditions.items():
            if isinstance(value, str):
                expressions.append(f'{field} == "{value}"')
            elif isinstance(value, (int, float)):
                expressions.append(f"{field} == {value}")
            elif isinstance(value, list):
                # IN condition
                if all(isinstance(v, str) for v in value):
                    value_str = '", "'.join(value)
                    expressions.append(f'{field} in ["{value_str}"]')
                else:
                    value_str = ", ".join(map(str, value))
                    expressions.append(f"{field} in [{value_str}]")
            elif isinstance(value, dict):
                # Range conditions
                if "gte" in value:
                    expressions.append(f'{field} >= {value["gte"]}')
                if "lte" in value:
                    expressions.append(f'{field} <= {value["lte"]}')
                if "gt" in value:
                    expressions.append(f'{field} > {value["gt"]}')
                if "lt" in value:
                    expressions.append(f'{field} < {value["lt"]}')

        return " and ".join(expressions) if expressions else None

    def _calculate_keyword_score(self, query: str, content: str) -> float:
        """Calculate keyword matching score."""

        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        matches = query_words.intersection(content_words)
        return len(matches) / len(query_words)

    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""

        try:
            collection = await self._get_collection(collection_name)

            # Safely check for indexes without causing ambiguous index error
            try:
                indexes = [index.index_name for index in collection.indexes]
                has_indexes = len(indexes) > 0
            except Exception as index_error:
                logger.warning(f"Could not get index info: {index_error}")
                indexes = []
                has_indexes = False

            stats = {
                "name": collection_name,
                "num_entities": collection.num_entities,
                "has_indexes": has_indexes,
                "indexes": indexes,
                "schema": {
                    "fields": [field.name for field in collection.schema.fields],
                    "description": collection.schema.description,
                },
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

    async def delete_by_filter(
        self, collection_name: str, filter_conditions: Dict[str, Any]
    ) -> bool:
        """Delete entities by filter conditions."""

        try:
            collection = await self._get_collection(collection_name)

            filter_expr = self._build_filter_expression(filter_conditions)
            if not filter_expr:
                logger.error("No valid filter expression provided")
                return False

            collection.delete(filter_expr)
            collection.flush()

            logger.info(f"Deleted entities matching filter: {filter_expr}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete entities: {e}")
            return False


# Factory function
def create_optimized_milvus_manager(
    connection_alias: str = "biblical_rag",
) -> OptimizedMilvusManager:
    """Create an optimized Milvus manager instance."""
    return OptimizedMilvusManager(connection_alias)
