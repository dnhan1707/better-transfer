from sqlalchemy.orm import Session
from app.db.connection import get_db
from RAG.services.knowledge_chunker import KnowledgeChunker
from RAG.services.embedding_services import EmbeddingService
from RAG.db.vector_store import VectorStore
from typing import List, Dict, Any

def create_vector_table(db: Session):
    VectorStore.create_vector_table(db)

async def process_chunks(db: Session, chunks: List[Dict[str, Any]], chunk_type: str):
    if not chunks:
        return 0
    
    texts = [chunk["content"] for chunk in chunks]

    embedding_service = EmbeddingService()
    embeddings = await embedding_service.batch_create_embedding(texts)

    for chunk in chunks:
        chunk["chunk_type"] = chunk_type
    
    VectorStore.insert_chunks(db, chunks, embeddings)
    return len(chunks)

async def insert_vectors(db: Session):
    """Insert all vectors into the database"""
    # Generate chunks from different sources
    course_chunks = await KnowledgeChunker.generate_course_chunker(db)
    articulation_chunks = await KnowledgeChunker.generate_articulation_chunker(db)
    prereq_chunks = await KnowledgeChunker.generate_prerequisite_chunker(db)
    
    # Process each chunk type
    total = 0
    total += await process_chunks(db, course_chunks, "course_description")
    total += await process_chunks(db, articulation_chunks, "articulation")
    total += await process_chunks(db, prereq_chunks, "prerequisite")
    
    return total
