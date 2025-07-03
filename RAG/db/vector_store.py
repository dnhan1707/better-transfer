from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from RAG.services.embedding_services import EmbeddingService
from RAG.config.settings import get_settings

class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.dimensions = settings.vector_store.embedding_dimensions
        self.table_name = settings.vector_store.table_name
        self.table_name_v2 = "knowledge_chunks_v2"
      

    async def create_vector_table_v2(self, vector_db: Session):
        vector_db.execute(
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
        vector_db.commit()


    async def vector_search_v2(self, vector_db: Session, input_text: str, target_combinations: List[Dict]):
        """Search for similar content using vector similarity across multiple targets"""
        embedding_service = EmbeddingService()
        embedded_text = await embedding_service.create_embedding(input_text)
        
        combined_results = []
        college_name = target_combinations[0]["college"]  # All have same source college
        
        # Get specific chunks for each university-major combination
        for target in target_combinations:
            university_name = target["university"]
            major_name = target["major"]
            
            specific_chunks = vector_db.execute(
                text(f"""
                SELECT 
                    id, content, college_name, university_name, major_name, chunk_type,
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
                    "source_college": college_name,
                    "target_university": university_name,
                    "target_major": major_name
                }
            ).fetchall()
            
            combined_results.extend(specific_chunks)
        
        # Get general course info (shared across all targets)
        general_chunks = vector_db.execute(
            text(f"""
            SELECT 
                id, content, college_name, university_name, major_name, chunk_type,
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
                "source_college": college_name
            }
        ).fetchall()
        
        # Combine and format results
        combined_results.extend(general_chunks)
        
        # Format results to include which target they're for
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
            for row in combined_results
        ]