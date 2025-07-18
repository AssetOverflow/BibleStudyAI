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

    # Service Connections
    KAFKA_BOOTSTRAP_SERVERS: List[str]
    DEEPHAVEN_SERVER: str
    MILVUS_HOST: str
    MILVUS_PORT: int

    # API Keys
    OPENAI_API_KEY: str
    XAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Application Settings
    PROJECT_NAME: str = "Chuck Missler AI Ministry"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
