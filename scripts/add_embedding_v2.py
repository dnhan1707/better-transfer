import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


load_dotenv()
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")

vector_store = VectorStore()
embedding_service = EmbeddingService()
chunker_service = ChunkerService()

async def process_seed_data(db):
    """Process course and prerequisite information from seed_data directory"""
    seed_dir = Path('RAG/db/seed_data')
    processed_files = 0
    
    print("\n=== PHASE 1: Processing class and prerequisite data ===\n")
    
    for json_path in seed_dir.glob("*.json"):
        print(f"Processing {json_path}")
        
        with json_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                
                # Extract data - using get() to handle missing fields
                college_name = data.get("community_college", "")
                course_name = data.get("course_name", "")
                code = data.get("code", "")
                
                # Content to be embedded - check if they exist and are lists
                classes = data.get("classes", [])
                prerequisites = data.get("prerequsites", [])  # Note the spelling in the original data files
                
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
                            "university_name": "",
                            "major_name": course_name,
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
                            "university_name": "",
                            "major_name": course_name,
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
    
    print(f"Completed processing {processed_files} files in Phase 1")
    return processed_files

async def process_articulation_data(db):
    """Process articulation mappings from seed_articulation directory"""
    seed_dir = Path('RAG/db/seed_articulation')
    processed_files = 0
    print("\n=== PHASE 2: Processing articulation data ===\n")
    
    for json_path in seed_dir.glob("*.json"):
        print(f"Processing {json_path}")
        
        with json_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                
                # Extract data for articulation mappings
                college_name = data.get("community_college", "")
                university_name = data.get("university", "")  # Note different field name
                major_name = data.get("major", "")
                
                # Get course mappings
                course_mappings = data.get("course_mapping", [])
                
                if course_mappings:
                    # Create embeddings for course mappings
                    mapping_embeddings = await embedding_service.batch_create_embedding(course_mappings)
                    
                    # Insert each mapping with its embedding
                    for idx, mapping_content in enumerate(course_mappings):
                        chunk = {
                            "content": mapping_content,
                            "college_name": college_name,
                            "university_name": university_name,
                            "major_name": major_name,
                            "chunk_type": "articulation"
                        }
                        await chunker_service.insert_chunk(db, chunk, mapping_embeddings[idx])
                
                processed_files += 1
                print(f"Successfully processed file: {json_path}")
                
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format in {json_path}")
            except Exception as e:
                print(f"Error processing {json_path}: {str(e)}")
                traceback.print_exc()
    
    print(f"Completed processing {processed_files} files in Phase 2")
    return processed_files

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
        
        # PHASE 1: Process seed_data
        seed_files = await process_seed_data(db)
        
        # PHASE 2: Process articulation data
        articulation_files = await process_articulation_data(db)
        
        print(f"\nSummary: Processed {seed_files} seed data files and {articulation_files} articulation files")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())