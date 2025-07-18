"""
Handles database connections and operations for TimescaleDB.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from utils.config import settings

load_dotenv()

# Defer engine creation to avoid import-time issues
engine = None
AsyncSessionLocal = None


def get_engine():
    global engine, AsyncSessionLocal
    if engine is None:
        # Explicitly use asyncpg
        database_url = settings.DATABASE_URL
        if not database_url.startswith("postgresql+asyncpg://"):
            # If it doesn't have the right scheme, fix it
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
            database_url = database_url.replace(
                "postgresql+psycopg://", "postgresql+asyncpg://"
            )
            database_url = database_url.replace(
                "postgresql+psycopg_async://", "postgresql+asyncpg://"
            )

        engine = create_async_engine(database_url, echo=True)
        AsyncSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
        )
    return engine


async def get_db():
    """
    Database dependency injector.
    """
    get_engine()  # Ensure engine is initialized
    async with AsyncSessionLocal() as session:
        yield session
