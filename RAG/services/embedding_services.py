import openai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.connection import get_db

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

class EmbeddingService:
    
    @staticmethod
    async def batch_create_embedding(texts: List[str]) -> List[List[float]]:
        try:
            response = await openai.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            return [item["embedding"] for item in response["data"]]

            
        except Exception as e:
            print(f"Error creating batch embeddings: {e}")
            raise
        