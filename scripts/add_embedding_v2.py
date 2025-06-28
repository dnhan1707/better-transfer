import sys
import os
import asyncio
from RAG.db.vector_store import VectorStore
from RAG.services.embedding_services import EmbeddingService
from RAG.services.chunker_service import ChunkerService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import json
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")

vector_store = VectorStore()
embedding_service = EmbeddingService()
chunker_service = ChunkerService()

async def main():
    """Main function to seed the database with course data"""
    # Connect to PostgreSQL
    engine = create_engine(
        RAG_DATABASE_URL, 
        connect_args={"options": "-c search_path=public"}
    )
       
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    
    try:
        # Create table if it doesn't exist
        await vector_store.create_vector_table_v2(db=db)

        seed_dir = Path('RAG/db/seed_data')
        processed_files = 0
        
        for json_path in seed_dir.glob("*.json"):
            print(f"Processing {json_path}")
            
            with json_path.open("r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    
                    # Extract data - using get() to handle missing fields
                    college_name = data.get("community_college", "")
                    course_name = data.get("course_name", "")
                    code = data.get("code", "")
                    university_name = data.get("university_name", "")
                    major_name = data.get("major_name", "")
                    
                    # Content to be embedded - check if they exist and are lists
                    classes = data.get("classes", [])
                    prerequisites = data.get("prerequisites", [])  # Corrected spelling
                    
                    if not isinstance(classes, list):
                        classes = [classes] if classes else []
                    
                    if not isinstance(prerequisites, list):
                        prerequisites = [prerequisites] if prerequisites else []
                    
                    # Process classes if they exist
                    if classes:
                        # Create embeddings for classes
                        class_embeddings = await embedding_service.batch_create_embedding(classes)
                        
                        # Insert each class with its embedding
                        for idx, class_content in enumerate(classes):
                            chunk = {
                                "content": class_content,
                                "college_name": college_name,
                                "university_name": university_name,
                                "major_name": major_name,
                                "chunk_type": "class"
                            }
                            await chunker_service.insert_chunk(db, chunk, class_embeddings[idx])
                    
                    # Process prerequisites if they exist
                    if prerequisites:
                        # Create embeddings for prerequisites
                        prereq_embeddings = await embedding_service.batch_create_embedding(prerequisites)
                        
                        # Insert each prerequisite with its embedding
                        for idx, prereq_content in enumerate(prerequisites):
                            chunk = {
                                "content": prereq_content,
                                "college_name": college_name,
                                "university_name": university_name,
                                "major_name": major_name,
                                "chunk_type": "prerequisite"
                            }
                            await chunker_service.insert_chunk(db, chunk, prereq_embeddings[idx])
                    
                    processed_files += 1
                    print(f"Successfully processed file: {json_path}")
                    
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON format in {json_path}")
                except Exception as e:
                    print(f"Error processing {json_path}: {str(e)}")
                    traceback.print_exc()
        
        print(f"Completed processing {processed_files} files")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())