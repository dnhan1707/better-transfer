import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from dotenv import load_dotenv
from RAG.db.prereqisite_graph import prerequisite_graph
from app.db.connection.mongo_connection import MongoDB

async def seed_mongodb():
    """Migrate prerequisite data from Python file to MongoDB"""
    print("Starting migration of prerequisite data to MongoDB...")

    mongo = MongoDB()
    collection = await mongo.get_collection("pcc_course_prerequisites")
    
    # Drop existing collection to start fresh
    collection.drop()
    
    # Create indexes
    collection.create_index([("college", 1), ("course_code", 1)], unique=True)
    collection.create_index([("department", 1)])
    

    # Prepare documents for batch insertion
    documents = []
    
    for college, courses in prerequisite_graph.items():
        print(f"Processing college: {college}")
        for course_code, course_data in courses.items():
            document = {
                "college": college,
                "course_code": course_code,
                "name": course_data["name"],
                "units": course_data["units"],
                "difficulty": course_data["difficulty"],
                "assessment_allow": course_data["assessment_allow"],
                "prerequisites": course_data["prerequisites"],
                "unlocks": course_data["unlocks"],
                "department": course_data["department"]
            }
            documents.append(document)
    
    # Insert all documents
    if documents:
        result = collection.insert_many(documents)
        print(f"Successfully migrated {len(result.inserted_ids)} course prerequisites to MongoDB")
    else:
        print("No documents to migrate")
    
    print("Migration completed")




if __name__ == "__main__":
    load_dotenv()
    asyncio.run(seed_mongodb())