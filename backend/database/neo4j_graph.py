"""
Handles database connections and operations for Neo4j.
"""

import os
from neo4j import AsyncGraphDatabase
from loguru import logger

from ..utils.config import settings


class Neo4jConnection:
    _driver = None

    @classmethod
    async def get_driver(cls):
        if cls._driver is None:
            try:
                logger.info(f"Connecting to Neo4j at {settings.NEO4J_URI}")
                cls._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
                await cls._driver.verify_connectivity()
                logger.success("Successfully connected to Neo4j.")
            except Exception as e:
                logger.opt(exception=True).error(f"Failed to connect to Neo4j: {e}")
                cls._driver = None  # Ensure driver is None on failure
        return cls._driver

    @classmethod
    async def close_driver(cls):
        if cls._driver is not None:
            try:
                await cls._driver.close()
                logger.info("Neo4j driver closed.")
            except Exception as e:
                logger.error(f"Failed to close Neo4j driver: {e}")
            finally:
                cls._driver = None


async def get_neo4j_session():
    """
    Neo4j session dependency injector.
    """
    driver = await Neo4jConnection.get_driver()
    if driver is None:
        logger.error("Cannot create Neo4j session, driver is not available.")
        yield None
        return

    async with driver.session() as session:
        yield session
