from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from functools import lru_cache
from app.utils.logging_config import get_logger
logger = get_logger(__name__)

import os

load_dotenv()

class LLMSettings(BaseModel):
    max_tokens: Optional[int] = None
    max_retries: int = Field(default=3)


class OpenAISettings(LLMSettings):
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    default_model: str = Field(default="gpt-4o-mini")
    embedding_model: str =  Field(default="text-embedding-3-small")

class DatabaseSettings(BaseModel):
    service_url: str = Field(default_factory=lambda: os.getenv("RAG_DATABASE_URL"))

class VectorStoreSettings(BaseModel):
    embedding_dimensions: int = 1536
    table_name: str = "knowledge_chunks"


class Settings(BaseModel):
    """This include all the settings"""
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)


@lru_cache
def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise

