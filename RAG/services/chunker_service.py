from typing import Dict
from sqlalchemy import text
from RAG.config.settings import get_settings
from typing import List


class ChunkerService():
    def __init__(self):
        settings = get_settings()
        self.dimensions = settings.vector_store.embedding_dimensions
        self.table_name = "knowledge_chunks_v2"  # Fixed variable name for consistency
        

    async def insert_chunk(self, db, chunk: Dict[str, any], embedding: List[float]):
        db.execute(
            text(f"""
            INSERT INTO {self.table_name}
            (content, college_name, university_name, major_name, chunk_type, embedding)
            VALUES
            (:content, :college_name, :university_name, :major_name, :chunk_type, :embedding)
            """),
            {
                "content": chunk["content"],
                "college_name": chunk.get("college_name"),
                "university_name": chunk.get("university_name"),
                "major_name": chunk.get("major_name"),
                "chunk_type": chunk["chunk_type"],
                "embedding": embedding
            }
        )
        db.commit()