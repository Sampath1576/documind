"""Configuration management for DocuMind"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")

    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", 1024))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", 0.0))

    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))
    MIN_CHUNK_SIZE: int = int(os.getenv("MIN_CHUNK_SIZE", 100))
    TOP_K: int = int(os.getenv("TOP_K", 4))

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    MAX_FILE_SIZE_BYTES: int = int(MAX_FILE_SIZE_MB) * 1024 * 1024
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    SUPPORTED_FORMATS: list = ["pdf", "txt", "docx"]

    # Vector Database
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # MLflow Configuration
    MLFLOW_TRACKING_URI: str = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://localhost:5000"
    )
    MLFLOW_EXPERIMENT_NAME: str = os.getenv(
        "MLFLOW_EXPERIMENT_NAME",
        "documind-rag"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load settings
settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)