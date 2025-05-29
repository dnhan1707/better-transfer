import sys
import os
import asyncio
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_db, get_vector_db
from RAG.services.embedding_services import EmbeddingService
from RAG.db.vector_store import VectorStore
from RAG.services.knowledge_chunker import KnowledgeChunker

async def extract_and_embed():
    """Extract data from application database and create embeddings in vector database"""
    app_db = get_db()
    vector_db = get_vector_db()
    
    try:
        print("Creating vector table if it doesn't exist...")
        VectorStore.create_vector_table(vector_db)
        
        # Use KnowledgeChunker to generate detailed chunks
        print("Generating course chunks...")
        course_chunks = await KnowledgeChunker.generate_course_chunker(app_db)
        print(f"Generated {len(course_chunks)} course chunks")
        
        print("Generating articulation chunks...")
        articulation_chunks = await KnowledgeChunker.generate_articulation_chunker(app_db)
        print(f"Generated {len(articulation_chunks)} articulation chunks")
        
        print("Generating prerequisite chunks...")
        prerequisite_chunks = await KnowledgeChunker.generate_prerequisite_chunker(app_db)
        print(f"Generated {len(prerequisite_chunks)} prerequisite chunks")
        
        # Combine all chunks
        all_chunks = course_chunks + articulation_chunks + prerequisite_chunks
        print(f"Total chunks to process: {len(all_chunks)}")
        
        # Generate embeddings in batches
        batch_size = 10
        total_processed = 0
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            contents = [chunk["content"] for chunk in batch]
            
            print(f"Generating embeddings for batch {i//batch_size + 1}...")
            embedding_service = EmbeddingService()
            embeddings = await embedding_service.batch_create_embedding(contents)            
            print(f"Storing {len(batch)} embeddings...")
            for j, chunk in enumerate(batch):
                VectorStore.insert_chunk(vector_db, chunk, embeddings[j])
                
            total_processed += len(batch)
            print(f"Progress: {total_processed}/{len(all_chunks)}")
        
        print(f"Successfully processed {total_processed} knowledge chunks!")
        
    finally:
        app_db.close()
        vector_db.close()

if __name__ == "__main__":
    asyncio.run(extract_and_embed())