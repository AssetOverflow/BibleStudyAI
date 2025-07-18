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

    # Redis Configuration
    REDIS_HOST: str = "redis-stack"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_DB: int = 0

    # Service Connections
    KAFKA_BOOTSTRAP_SERVERS: str
    DEEPHAVEN_SERVER: str
    MILVUS_HOST: str
    MILVUS_PORT: int

    # API Keys
    OPENAI_API_KEY: str
    XAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Application Settings
    PROJECT_NAME: str = "BibleStudyAI"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


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
OPENAI_API_KEY = settings.OPENAI_API_KEY
