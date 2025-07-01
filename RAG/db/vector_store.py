from sqlalchemy import text
from typing import Dict, Any, List
from RAG.services.embedding_services import EmbeddingService
from app.schemas.transferPlanRequest import TransferPlanRequest
from RAG.config.settings import get_settings
from app.db.connection import get_vector_db

class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.dimensions = settings.vector_store.embedding_dimensions
        self.table_name = settings.vector_store.table_name
        self.table_name_v2 = "knowledge_chunks_v2"
        self.vector_db = get_vector_db()
      
        
    async def create_vector_table(self):
        self.vector_db.execute(
            text(f"""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR({self.dimensions}),  
                college_id INTEGER,
                college_name TEXT,
                university_id INTEGER,
                university_name TEXT,
                major_id INTEGER,
                major_name TEXT,
                chunk_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX ON {self.table_name} USING hnsw (embedding vector_cosine_ops);
            """)
        )
        self.vector_db.commit()
    

    async def create_vector_table_v2(self):
        self.vector_db.execute(
            text(f"""
            CREATE EXTENSION IF NOT EXISTS vector;
            DROP TABLE IF EXISTS {self.table_name_v2};
            CREATE TABLE IF NOT EXISTS {self.table_name_v2} (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                college_name TEXT,
                university_name TEXT,
                major_name TEXT,
                chunk_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                embedding VECTOR({self.dimensions})
            );

            -- Vector similarity index
            CREATE INDEX ON {self.table_name_v2} USING hnsw (embedding vector_cosine_ops);
            
            -- Column indexes for faster filtering
            CREATE INDEX idx_{self.table_name_v2}_college ON {self.table_name_v2} (college_name);
            CREATE INDEX idx_{self.table_name_v2}_university ON {self.table_name_v2} (university_name);
            CREATE INDEX idx_{self.table_name_v2}_major ON {self.table_name_v2} (major_name);
            CREATE INDEX idx_{self.table_name_v2}_chunk_type ON {self.table_name_v2} (chunk_type);
            
            -- Composite index for common filter combinations
            CREATE INDEX idx_{self.table_name_v2}_college_chunk ON {self.table_name_v2} (college_name, chunk_type);
            """)
        )
        self.vector_db.commit()


    async def insert_chunk(self, chunk: Dict[str, Any], embedding: List[float]):
        """Insert a single chunk with embedding into the vector database"""
        self.vector_db.execute(
            text(f"""
            INSERT INTO {self.table_name}
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
        self.vector_db.commit()


    async def insert_chunks(self, chunks: List[Dict[str, Any]],  embeddings: List[List[float]]):
        # Insert multiple chunks
        for i, chunk in enumerate(chunks):
            await self.insert_chunk(chunk, embeddings[i])

        self.vector_db.commit()
        

    async def vector_search(self, input_text: str, transferRequest: TransferPlanRequest):
        """
        Search for similar content using vector similarity
        """
        embedding_service = EmbeddingService()
        embedded_text = await embedding_service.create_embedding(input_text)

        # Specific chunks for articulation / major-university match
        specific_chunks = self.vector_db.execute(
            text(f"""
            SELECT 
                id,
                content, 
                college_name, 
                university_name, 
                major_name, 
                chunk_type,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM 
                {self.table_name}
            WHERE 
                college_id = :source_college
                AND university_id = :target_university
                AND major_id = :target_major 
            ORDER BY 
                embedding <=> CAST(:query_embedding AS vector)
            LIMIT 30
            """),
            {
                "query_embedding": embedded_text,
                "source_college": transferRequest.college_id,
                "target_university": transferRequest.university_id,
                "target_major": transferRequest.major_id,
            }
        ).fetchall()

        # General course info (description + prerequisite)
        general_chunks = self.vector_db.execute(
            text(f"""
            SELECT 
                id,
                content, 
                college_name, 
                university_name, 
                major_name, 
                chunk_type,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM 
                {self.table_name}
            WHERE 
                college_id = :source_college
                AND chunk_type IN ('course_description', 'prerequisite')
            ORDER BY 
                embedding <=> CAST(:query_embedding AS vector)
            LIMIT 30
            """),
            {
                "query_embedding": embedded_text,
                "source_college": transferRequest.college_id,
            }
        ).fetchall()

        # Combine results
        combined = specific_chunks + general_chunks

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
            for row in combined
        ]


    async def vector_search_v2(self, input_text: str, basic_info: Dict[str, Any]):
        """
        Search for similar content using vector similarity
        """
        embedding_service = EmbeddingService()
        embedded_text = await embedding_service.create_embedding(input_text)
        
        # Specific chunks for articulation / major-university match
        specific_chunks = self.vector_db.execute(
            text(f"""
            SELECT 
                id,
                content, 
                college_name, 
                university_name, 
                major_name, 
                chunk_type,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM 
                {self.table_name_v2}
            WHERE 
                college_name = :source_college
                AND university_name = :target_university
                AND major_name = :target_major 
            ORDER BY 
                embedding <=> CAST(:query_embedding AS vector)
            """),
            {
                "query_embedding": embedded_text,
                "source_college": basic_info["college"].college_name,
                "target_university": basic_info["university"].university_name,
                "target_major": basic_info["major"].major_name
            }
        ).fetchall()

        # General course info (description + prerequisite)
        general_chunks = self.vector_db.execute(
            text(f"""
            SELECT 
                id,
                content, 
                college_name, 
                university_name, 
                major_name, 
                chunk_type,
                1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
            FROM 
                {self.table_name_v2}
            WHERE 
                college_name = :source_college
                AND chunk_type IN ('class', 'prerequisite')
            ORDER BY 
                embedding <=> CAST(:query_embedding AS vector)
            """),
            {
                "query_embedding": embedded_text,
                "source_college": basic_info["college"].college_name
            }
        ).fetchall()

        # Combine results
        combined = specific_chunks + general_chunks
        self.vector_db.close()
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
            for row in combined
        ]
