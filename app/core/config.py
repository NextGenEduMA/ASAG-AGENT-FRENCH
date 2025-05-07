import os
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ASAG Agent"

    # Paramètres d'environnement supplémentaires
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/asag.log"

    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "asag_db")

    # NLP Model settings
    # Modèle principal (LLM)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "huggingface")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
    LLM_API_ENDPOINT: str = os.getenv("LLM_API_ENDPOINT", "")

    # Modèle d'embedding
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")

    # Modèle d'évaluation
    NLP_MODEL_PATH: str = os.getenv("NLP_MODEL_PATH", "camembert-base")
    USE_GPU: bool = os.getenv("USE_GPU", "False").lower() == "true"

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:8000",  # Backend for testing
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Optionnellement, vous pouvez permettre des champs supplémentaires


settings = Settings()