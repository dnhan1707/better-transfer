from openai import OpenAI
import os
from typing import List
from dotenv import load_dotenv
from app.utils.logging_config import get_logger
from RAG.config.settings import get_settings

logger = get_logger(__name__)

class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        self.model = settings.openai.embedding_model
        self.client = OpenAI(api_key=settings.openai.api_key)


    async def batch_create_embedding(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            return embeddings
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {e}")
            raise

    async def create_embedding(self, texts: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
