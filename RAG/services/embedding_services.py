from InstructorEmbedding import INSTRUCTOR
from typing import List
import torch

class EmbeddingService:
    def __init__(self, instruction: str):
        self.model = INSTRUCTOR('hkunlp/instructor-xl')
        self.instruction = instruction

    async def batch_create_embedding(self, texts: List[str]) -> List[List[float]]:
        try:
            instruction_text_pair = [[self.instruction, text] for text in texts]
            batch_size = 32
            embeddings = []
            for i in range(0, len(instruction_text_pair), batch_size):
                batch = instruction_text_pair[i: i + batch_size]
                with torch.no_grad():
                    embedding = self.model.encode(batch)
                    embeddings.extend([emb.tolist() for emb in embedding])
            
            return embeddings
        except Exception as e:
            print(f"Error creating batch embeddings: {e}")
            raise
        