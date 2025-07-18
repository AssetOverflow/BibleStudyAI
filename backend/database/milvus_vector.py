"""
Handles database connections and operations for Milvus.
"""

import os
from pymilvus import connections, utility
from loguru import logger

from ..utils.config import settings


def get_milvus_connection():
    """
    Milvus connection dependency injector.
    """
    alias = "default"
    if not utility.has_connection(alias):
        try:
            logger.info(
                f"Connecting to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
            )
            connections.connect(
                alias=alias, host=settings.MILVUS_HOST, port=settings.MILVUS_PORT
            )
            logger.success("Successfully connected to Milvus.")
        except Exception as e:
            logger.opt(exception=True).error(f"Failed to connect to Milvus: {e}")
            return None
    return connections.get_connection(alias)


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
