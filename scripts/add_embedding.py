import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from RAG.services.insert_vectors import insert_vectors
from RAG.db.vector_store import VectorStore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")

vector_store = VectorStore()

async def main():
    """Main function to seed the database"""
    # Connect to Docker PostgreSQL instead of local
    engine = create_engine(
        RAG_DATABASE_URL, 
        connect_args={"options": "-c search_path=public"}
    )
       
    DockerSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = DockerSession()
    
    try:
        await vector_store.create_vector_table(db)  
        count = await insert_vectors(db)
        print(f"Successfully inserted {count} vector chunks into the database")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())