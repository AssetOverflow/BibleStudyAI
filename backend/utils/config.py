"""
Centralized configuration management using Pydantic's BaseSettings.
Ensures that all required environment variables are present and correctly typed.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database URLs
    DATABASE_URL: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    REDIS_URL: str

    # PostgreSQL Configuration
    POSTGRES_HOST: str = "timescaledb"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "H0lySp1r1t!"
    POSTGRES_DB: str = "biblestudyai"

    # Redis Configuration
    REDIS_HOST: str = "redis-stack"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0
    REDIS_TS_DB: int = 0

    # Milvus Configuration
    MILVUS_HOST: str
    MILVUS_PORT: int
    MILVUS_USER: str = "milvus"
    MILVUS_PASSWORD: str = "milvus_password"
    MILVUS_ALIAS: str = "default"

    # Service Connections
    KAFKA_BOOTSTRAP_SERVERS: str
    DEEPHAVEN_SERVER: str

    # API Keys
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_ORGANIZATION: str = "org-tc9Cql7ES5CtTIjG8THIKrXN"
    OPENAI_PROJECT_ID: str = "proj_dBm8ZqXT64L1sKTbdyvIw51n"

    XAI_API_KEY: str
    XAI_API_BASE: str = "https://api.xai.com/v1"

    ANTHROPIC_API_KEY: str
    GEMINI_API_KEY: str = "AIzaSyBhUe1CfGjNkyDb1-9tK13k5d11nJ8IsYY"

    # Application Settings
    PROJECT_NAME: str = "BibleStudyAI"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables


settings = Settings()

# Export commonly used settings
DATABASE_URL = settings.DATABASE_URL
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_DB = settings.REDIS_DB
MILVUS_HOST = settings.MILVUS_HOST
MILVUS_PORT = settings.MILVUS_PORT
MILVUS_ALIAS = settings.MILVUS_ALIAS
OPENAI_API_KEY = settings.OPENAI_API_KEY
