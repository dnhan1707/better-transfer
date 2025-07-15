import os
import sys
import csv
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from app.db.connection.mongo_connection import MongoDB

async def seed_vector_db_from_csv(csv_file_path: str):
    """Seed vector_db database with data from CSV file"""
    print(f"Starting migration from CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    # Connect to vector_db database
    mongo = MongoDB("vector_db")
    collection = mongo.get_collection("knowledge_chunks")
    
    # Optional: Drop existing collection to start fresh
    # Uncomment the next line if you want to clear existing data
    # await collection.drop()
    
    # Create indexes for better performance
    await collection.create_index([("id", 1)], unique=True)
    await collection.create_index([("college_name", 1)])
    await collection.create_index([("university_name", 1)])
    await collection.create_index([("major_name", 1)])
    await collection.create_index([("chunk_type", 1)])
    await collection.create_index([("created_at", 1)])
    
    documents = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_number, row in enumerate(reader, start=1):
                try:
                    # Parse embedding from string to list if it's stored as JSON string
                    embedding = row['embedding']
                    if isinstance(embedding, str):
                        try:
                            embedding = json.loads(embedding)
                        except json.JSONDecodeError:
                            print(f"Warning: Could not parse embedding for row {row_number}, skipping...")
                            continue
                    
                    # Parse created_at if it's a string
                    created_at = row['created_at']
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except ValueError:
                            try:
                                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                created_at = datetime.now()
                    
                    document = {
                        "id": row['id'],
                        "content": row['content'],
                        "college_name": row['college_name'],
                        "university_name": row['university_name'],
                        "major_name": row['major_name'],
                        "chunk_type": row['chunk_type'],
                        "created_at": created_at,
                        "embedding": embedding
                    }
                    
                    documents.append(document)
                    
                    # Insert in batches of 1000 for better performance
                    if len(documents) >= 1000:
                        await insert_batch(collection, documents)
                        documents = []
                        
                except Exception as e:
                    print(f"Error processing row {row_number}: {e}")
                    continue
            
            # Insert remaining documents
            if documents:
                await insert_batch(collection, documents)
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Get final count
    total_count = await collection.count_documents({})
    print(f"Migration completed. Total documents in collection: {total_count}")

async def insert_batch(collection, documents: List[Dict[str, Any]]):
    """Insert a batch of documents into the collection"""
    try:
        result = await collection.insert_many(documents, ordered=False)
        print(f"Successfully inserted batch of {len(result.inserted_ids)} documents")
    except Exception as e:
        print(f"Error inserting batch: {e}")

async def main():
    """Main function to run the seeding process"""
    load_dotenv()
    
    # Update this path to your CSV file location
    csv_file_path = "csv_exports/vector_db/knowledge_chunks_v2.csv"
    
    await seed_vector_db_from_csv(csv_file_path)
    
    # Close the connection
    mongo = MongoDB("vector_db")
    mongo.close_connection()

if __name__ == "__main__":
    asyncio.run(main())