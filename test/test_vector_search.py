import sys
import os
import asyncio

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from RAG.db.vector_store import VectorStore

async def main():
    """Test vector search functionality"""
    db = get_vector_db()
    try:
        # Sample query
        query = "What prerequisites do I need for Computer Science courses?"
        print(f"Searching for: '{query}'")
        
        # Perform vector search
        results = await VectorStore.vector_search(db, query)
        
        # Display results
        print("\nSearch Results:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i}. Similarity: {result['similarity']:.4f}")
            if result['college_name']:
                print(f"   College: {result['college_name']}")
            if result['university_name']:
                print(f"   University: {result['university_name']}")
            if result['major_name']:
                print(f"   Major: {result['major_name']}")
            print(f"   Type: {result['chunk_type']}")
            print(f"   Content: {result['content']}")
            print("-" * 80)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())