import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from scripts.seed_scripts.seed_maindb import main as seed_main_db
from scripts.seed_scripts.seed_vectordb import main as seed_vector_db
from scripts.seed_scripts.seed_embedded_cache import main as seed_embedding_cache
from seed_mongo_db import seed_mongodb  # Original course prerequisite seeding

async def main():
    """Main function to seed all MongoDB databases"""
    load_dotenv()
    
    print("=" * 60)
    print("Starting complete MongoDB seeding process...")
    print("=" * 60)
    
    try:
        # 1. Seed main database (colleges, universities, majors)
        print("\n1. Seeding main database...")
        await seed_main_db()
        
        # 2. Seed vector database (knowledge chunks)
        # print("\n2. Seeding vector database with knowledge chunks...")
        # await seed_vector_db()
        
        # 3. Seed embedding cache
        # print("\n3. Seeding embedding cache...")
        # await seed_embedding_cache()
        
        # 4. Seed course prerequisites (original)
        # print("\n4. Seeding course prerequisites...")
        # await seed_mongodb()
        
        print("\n" + "=" * 60)
        print("All MongoDB databases seeded successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during seeding process: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())