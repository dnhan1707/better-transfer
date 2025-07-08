from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib


class CachingService:
    async def create_cache_table(self, vector_db: Session):
        vector_db.execute(
            text("""
                CREATE TABLE embedding_cache (
                    content_hash TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(1536) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""")
        )
    

    async def get_cached_embedding(self, vector_db: Session, content: str):
        content_hash = self._hash_content(content)
        query = """
            SELECT embedding FROM embedding_cache 
            WHERE content_hash = :content_hash
            """
        res = vector_db.execute(
            text(query),
            {"content_hash": content_hash}
        )
        row = res.fetchone()
        return row[0] if row else None


    async def cache_embedding(self, vector_db: Session, content: str, embedding):
        content_hash = self._hash_content(content)
        query = """
            INSERT INTO embedding_cache (content_hash, content, embedding)
            VALUES (:content_hash, :content, :embedding)
            ON CONFLICT (content_hash) DO NOTHING
            """
        vector_db.execute(text(query), {
            "content_hash": content_hash, 
            "content": content,
            "embedding": embedding
        })
        vector_db.commit()

    def _hash_content(self, content):
        """Create normalized hash of content for lookup"""
        normalized = content.strip().lower()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()