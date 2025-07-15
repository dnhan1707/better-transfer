import os
import sys
import csv
import asyncio
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from app.db.connection.mongo_connection import MongoDB

async def seed_colleges_from_csv(csv_file_path: str):
    """Seed colleges collection with data from CSV file"""
    print(f"Starting migration of colleges from CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    # Connect to main_db database
    mongo = MongoDB("main_db")
    collection = mongo.get_collection("colleges")
    
    # Optional: Drop existing collection to start fresh
    # await collection.drop()
    
    # Create indexes
    await collection.create_index([("id", 1)], unique=True)
    await collection.create_index([("college_name", 1)], unique=True)
    
    documents = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_number, row in enumerate(reader, start=1):
                try:
                    document = {
                        "id": int(row['id']),
                        "college_name": row['college_name']
                    }
                    documents.append(document)
                    
                except Exception as e:
                    print(f"Error processing row {row_number}: {e}")
                    continue
            
            # Insert all documents
            if documents:
                await insert_batch(collection, documents, "colleges")
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Get final count
    total_count = await collection.count_documents({})
    print(f"Colleges migration completed. Total documents: {total_count}")

async def seed_universities_from_csv(csv_file_path: str):
    """Seed universities collection with data from CSV file"""
    print(f"Starting migration of universities from CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    # Connect to main_db database
    mongo = MongoDB("main_db")
    collection = mongo.get_collection("universities")
    
    # Optional: Drop existing collection to start fresh
    # await collection.drop()
    
    # Create indexes
    await collection.create_index([("id", 1)], unique=True)
    await collection.create_index([("university_name", 1)], unique=True)
    await collection.create_index([("is_uc", 1)])
    
    documents = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_number, row in enumerate(reader, start=1):
                try:
                    # Convert is_uc to boolean
                    is_uc = row['is_uc'].lower() in ('true', '1', 'yes')
                    
                    document = {
                        "id": int(row['id']),
                        "university_name": row['university_name'],
                        "is_uc": is_uc
                    }
                    documents.append(document)
                    
                except Exception as e:
                    print(f"Error processing row {row_number}: {e}")
                    continue
            
            # Insert all documents
            if documents:
                await insert_batch(collection, documents, "universities")
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Get final count
    total_count = await collection.count_documents({})
    print(f"Universities migration completed. Total documents: {total_count}")

async def seed_majors_from_csv(csv_file_path: str):
    """Seed majors collection with data from CSV file"""
    print(f"Starting migration of majors from CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    # Connect to main_db database
    mongo = MongoDB("main_db")
    collection = mongo.get_collection("majors")
    
    # Optional: Drop existing collection to start fresh
    # await collection.drop()
    
    # Create indexes
    await collection.create_index([("id", 1)], unique=True)
    await collection.create_index([("major_name", 1)])
    
    documents = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_number, row in enumerate(reader, start=1):
                try:
                    document = {
                        "id": int(row['id']),
                        "major_name": row['major_name']
                    }
                    documents.append(document)
                    
                except Exception as e:
                    print(f"Error processing row {row_number}: {e}")
                    continue
            
            # Insert all documents
            if documents:
                await insert_batch(collection, documents, "majors")
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Get final count
    total_count = await collection.count_documents({})
    print(f"Majors migration completed. Total documents: {total_count}")

async def insert_batch(collection, documents: List[Dict[str, Any]], collection_name: str):
    """Insert a batch of documents into the collection"""
    try:
        result = await collection.insert_many(documents, ordered=False)
        print(f"Successfully inserted {len(result.inserted_ids)} {collection_name} documents")
    except Exception as e:
        print(f"Error inserting {collection_name} batch: {e}")

async def main():
    """Main function to run the seeding process"""
    load_dotenv()
    
    # Define CSV file paths
    csv_files = {
        "colleges": "csv_exports/main_db/colleges.csv",
        "universities": "csv_exports/main_db/universities.csv", 
        "majors": "csv_exports/main_db/majors.csv"
    }
    
    # Seed each collection
    await seed_colleges_from_csv(csv_files["colleges"])
    await seed_universities_from_csv(csv_files["universities"])
    await seed_majors_from_csv(csv_files["majors"])
    
    print("\nAll main_db collections seeded successfully!")
    
    # Close the connection
    mongo = MongoDB("main_db")
    mongo.close_connection()

if __name__ == "__main__":
    asyncio.run(main())