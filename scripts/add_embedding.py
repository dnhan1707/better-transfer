import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from RAG.insert_vectors import insert_vectors, create_vector_table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

async def main():
    """Main function to seed the database"""
    # Connect to Docker PostgreSQL instead of local
    engine = create_engine("postgresql+psycopg2://postgres:nhancho1707@localhost:5433/postgres", 
                      connect_args={"options": "-c search_path=public"})   
    DockerSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = DockerSession()
    
    try:
        create_vector_table(db)  
        count = await insert_vectors(db)
        print(f"Successfully inserted {count} vector chunks into the database")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())