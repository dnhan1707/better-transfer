import sys
import os
import asyncio
from sqlalchemy import text
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_db, get_vector_db
from RAG.services.embedding_services import EmbeddingService
from RAG.db.vector_store import VectorStore

async def extract_and_embed():
    """Extract data from application database and create embeddings in vector database"""
    app_db = get_db()
    vector_db = get_vector_db()
    
    try:
        print("Creating vector table if it doesn't exist...")
        VectorStore.create_vector_table(vector_db)
        # Extract courses data
        print("Extracting courses data...")
        courses_query = text("""
            SELECT c.id AS course_id, c.code, c.name AS course_name, c.units, c.difficulty,
                   col.id AS college_id, col.college_name
            FROM courses c
            JOIN colleges col ON c.college_id = col.id
        """)
        courses = app_db.execute(courses_query).fetchall()
        print(f"Found {len(courses)} courses")
        
        # Extract articulation data
        print("Extracting articulation data...")
        articulation_query = text("""
            SELECT a.id, a.name, 
                   u.id AS university_id, u.university_name,
                   m.id AS major_id, m.major_name,
                   col.id AS college_id, col.college_name
            FROM articulation_group a
            JOIN universities u ON a.university_id = u.id
            JOIN majors m ON a.major_id = m.id
            JOIN colleges col ON a.college_id = col.id
        """)
        articulations = app_db.execute(articulation_query).fetchall()
        print(f"Found {len(articulations)} articulations")
        
        # Process courses into chunks
        course_chunks = []
        for course in courses:
            chunk = {
                "content": f"Course {course.code}: {course.course_name} at {course.college_name} is worth {course.units} units with difficulty level {course.difficulty}.",
                "college_id": course.college_id,
                "college_name": course.college_name,
                "university_id": None, 
                "university_name": None,
                "major_id": None,
                "major_name": None,
                "chunk_type": "course_description"
            }
            course_chunks.append(chunk)
            
        # Process articulations into chunks
        articulation_chunks = []
        for art in articulations:
            chunk = {
                "content": f"To transfer from {art.college_name} to {art.university_name} for {art.major_name}, follow the articulation requirements: {art.name}",
                "college_id": art.college_id,
                "college_name": art.college_name,
                "university_id": art.university_id,
                "university_name": art.university_name,
                "major_id": art.major_id,
                "major_name": art.major_name,
                "chunk_type": "articulation"
            }
            articulation_chunks.append(chunk)
        
        # Combine all chunks
        all_chunks = course_chunks + articulation_chunks
        
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