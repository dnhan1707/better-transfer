import openai
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class EmbeddingService:
    def __init__(self):
        self.model = "text-embedding-ada-002"

    async def batch_create_embedding(self, texts: List[str]) -> List[List[float]]:
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            return embeddings
        except Exception as e:
            print(f"Error creating batch embeddings: {e}")
            raise

    async def create_embedding(self, texts: str) -> List[float]:
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=texts
            )

            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print(f"Error creating batch embeddings: {e}")
            raise
