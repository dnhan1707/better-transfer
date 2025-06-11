import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from RAG.db.vector_store import VectorStore
from sqlalchemy import text  # Import the text function

def main():
    """Initialize the vector database with required tables"""
    db = get_vector_db()
    try:
        print("Creating vector extension...")
        # Ensure vector extension is created - FIX HERE
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        
        print("Creating vector table...")
        VectorStore.create_vector_table(db)
        print("Vector table created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    main()