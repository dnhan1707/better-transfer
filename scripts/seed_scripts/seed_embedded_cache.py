import os
import sys
import csv
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from app.db.connection.mongo_connection import MongoDB

async def seed_embedding_cache_from_csv(csv_file_path: str):
    """Seed embedding_cache collection with data from CSV file"""
    print(f"Starting migration of embedding cache from CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    # Connect to vector_db database
    mongo = MongoDB("vector_db")
    collection = mongo.get_collection("embedding_cache")
    
    # Optional: Drop existing collection to start fresh
    # Uncomment the next line if you want to clear existing data
    # await collection.drop()
    
    # Create indexes for better performance
    await collection.create_index([("content_hash", 1)], unique=True)
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
                    
                    # Parse created_at if it exists and is a string
                    created_at = datetime.now()  # Default value
                    if 'created_at' in row and row['created_at']:
                        created_at_str = row['created_at']
                        if isinstance(created_at_str, str):
                            try:
                                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            except ValueError:
                                try:
                                    created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    created_at = datetime.now()
                    
                    document = {
                        "content_hash": row['content_hash'],
                        "content": row['content'],
                        "embedding": embedding,
                        "created_at": created_at
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
    print(f"Embedding cache migration completed. Total documents in collection: {total_count}")

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
    
    # Path to the embedding cache CSV file
    csv_file_path = "csv_exports/vector_db/embedding_cache.csv"
    
    await seed_embedding_cache_from_csv(csv_file_path)
    
    # Close the connection
    mongo = MongoDB("vector_db")
    mongo.close_connection()

if __name__ == "__main__":
    asyncio.run(main())