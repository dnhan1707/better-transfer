from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List

class VectorStore:
    @staticmethod
    def create_vector_table(db: Session):
        db.execute(
            text("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR(1536),  
                college_id INTEGER,
                college_name TEXT,
                university_id INTEGER,
                university_name TEXT,
                major_id INTEGER,
                major_name TEXT,
                chunk_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
            """)
        )
        db.commit()

    @staticmethod
    def insert_chunk(db: Session, chunk: Dict[str, Any], embedding: list[float]):
        # Insert one chunk
        db.execute(
            text("""
            INSERT INTO knowledge_chunks
            (content, embedding, college_id, college_name, university_id, university_name, 
            major_id, major_name, chunk_type)
            VALUES
            (:content, :embedding, :college_id, :college_name, :university_id, :university_name,
            :major_id, :major_name, :chunk_type)
            """),
            {
                "content": chunk["content"],
                "embedding": embedding,
                "college_id": chunk.get("college_id"),
                "college_name": chunk.get("college_name"),
                "university_id": chunk.get("university_id"),
                "university_name": chunk.get("university_name"),
                "major_id": chunk.get("major_id"),
                "major_name": chunk.get("major_name"),
                "chunk_type": chunk.get("chunk_type"),
            }
        )

    @staticmethod
    def insert_chunks(db: Session, chunks: List[Dict[str, Any]],  embeddings: List[List[float]]):
        # Insert multiple chunks
        for i, chunk in enumerate(chunks):
            VectorStore.insert_chunk(db, chunk, embeddings[i])

        db.commit()
        

