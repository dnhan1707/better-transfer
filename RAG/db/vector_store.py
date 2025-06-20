from sqlalchemy import text
from typing import Dict, Any, List
from RAG.services.embedding_services import EmbeddingService
from app.schemas.transferPlanRequest import TransferPlanRequest

class VectorStore:
    def __init__(self):
        pass
        
    async def create_vector_table(self, db):
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

    async def insert_chunk(self, db, chunk: Dict[str, Any], embedding: List[float]):
        """Insert a single chunk with embedding into the vector database"""
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
                "chunk_type": chunk.get("chunk_type", "general"),
            }
        )
        db.commit()

    async def insert_chunks(self, db, chunks: List[Dict[str, Any]],  embeddings: List[List[float]]):
        # Insert multiple chunks
        for i, chunk in enumerate(chunks):
            await self.insert_chunk(db, chunk, embeddings[i])

        db.commit()
        
    async def vector_search(self, db, input_text: str, transferRequest: TransferPlanRequest):
        """
        Search for similar content using vector similarity
        
        Args:
            db: Database session
            input_text: Query text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results with similarity scores
        """
        embedding_service = EmbeddingService()
        embedded_text = await embedding_service.create_embedding(input_text)
        # Use the <=> operator for cosine distance (lower is more similar)
        results = db.execute(
            text("""
            SELECT 
                id,
                content, 
                college_name, 
                university_name, 
                major_name, 
                chunk_type,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM 
                knowledge_chunks
            WHERE 
                college_id = :source_college
            ORDER BY 
                embedding <=> CAST(:query_embedding AS vector)
            """),
            {
                "query_embedding": embedded_text,
                "source_college": transferRequest.college_id,
                "target_university": transferRequest.university_id,
                "target_major": transferRequest.major_id,
            }
        ).fetchall()
        
        # Convert results to a list of dictionaries
        return [
            {
                "id": row[0],
                "content": row[1],
                "college_name": row[2],
                "university_name": row[3],
                "major_name": row[4],
                "chunk_type": row[5],
                "similarity": row[6]
            }
            for row in results
        ]