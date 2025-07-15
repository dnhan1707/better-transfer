from typing import Dict, Any, List
from RAG.services.embedding_services import EmbeddingService
from RAG.config.settings import get_settings
from app.db.connection.mongo_connection import MongoDB

class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.dimensions = settings.vector_store.embedding_dimensions
        self.collection_name = "knowledge_chunks"
        self.mongo = MongoDB("vector_db")

    async def create_vector_collection(self):
        """Create indexes for the vector collection"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            # Create indexes for better performance
            await collection.create_index([("college_name", 1)])
            await collection.create_index([("university_name", 1)])
            await collection.create_index([("major_name", 1)])
            await collection.create_index([("chunk_type", 1)])
            await collection.create_index([("created_at", 1)])
            
            # Composite indexes for common filter combinations
            await collection.create_index([("college_name", 1), ("chunk_type", 1)])
            await collection.create_index([("college_name", 1), ("university_name", 1), ("major_name", 1)])
            
            print(f"Vector collection '{self.collection_name}' indexes created successfully")
            
        except Exception as e:
            print(f"Error creating vector collection indexes: {e}")

    async def vector_search_v2(self, input_text: str, target_combinations: List[Dict]):
        """Search for similar content using vector similarity across multiple targets"""        
        combined_results = await self.get_specific_chunks(target_combinations)
        general_chunks = await self.get_general_chunks(target_combinations, input_text)
        combined_results.extend(general_chunks)
        
        return [
            {
                "id": doc.get("id"),
                "content": doc.get("content"),
                "college_name": doc.get("college_name"),
                "university_name": doc.get("university_name"),
                "major_name": doc.get("major_name"),
                "chunk_type": doc.get("chunk_type"),
                "similarity": doc.get("similarity", 0)
            }
            for doc in combined_results
        ]
    
    async def get_courses_data(self, source_college: str):
        """Get course data for a specific college"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            # Query for courses and prerequisites
            cursor = collection.find({
                "college_name": source_college,
                "chunk_type": {"$in": ["class", "prerequisite"]}
            })
            
            courses_data = []
            async for doc in cursor:
                courses_data.append({
                    "id": doc.get("id"),
                    "content": doc.get("content"),
                    "college_name": doc.get("college_name"),
                    "university_name": doc.get("university_name"),
                    "major_name": doc.get("major_name"),
                    "chunk_type": doc.get("chunk_type"),
                })
            
            return courses_data
            
        except Exception as e:
            print(f"Error getting courses data: {e}")
            return []

    async def get_specific_chunks(self, target_combinations: List[Dict]):
        """Get specific articulation chunks for target combinations"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            combined_results = []
            college_name = target_combinations[0]["college"]  # All have same source college
            
            # Get specific chunks for each university-major combination
            for target in target_combinations:
                university_name = target["university"]
                major_name = target["major"]
                
                # Query for specific articulation chunks
                cursor = collection.find({
                    "college_name": college_name,
                    "university_name": university_name,
                    "major_name": major_name,
                    "chunk_type": "articulation"
                })
                
                async for doc in cursor:
                    doc["similarity"] = 1.0  # Add similarity score
                    doc.pop('_id', None)  # Remove MongoDB _id
                    combined_results.append(doc)

            return combined_results
            
        except Exception as e:
            print(f"Error getting specific chunks: {e}")
            return []

    async def get_general_chunks(self, target_combinations: List[Dict], input_text: str):
        """Get general chunks using vector similarity search"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            combined_results = []
            embedding_service = EmbeddingService()
            
            # Create embedding for input text
            embedded_text = await embedding_service.create_embedding(input_text)
            college_name = target_combinations[0]["college"]  # All have same source college

            # MongoDB vector search pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",  # You'll need to create this index in MongoDB Atlas
                        "path": "embedding",
                        "queryVector": embedded_text,
                        "numCandidates": 100,
                        "limit": 50
                    }
                },
                {
                    "$match": {
                        "college_name": college_name,
                        "chunk_type": {"$in": ["class", "prerequisite"]}
                    }
                },
                {
                    "$addFields": {
                        "similarity": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$sort": {"similarity": -1}
                }
            ]
            
            # If vector search is not available, fall back to regular search
            try:
                cursor = collection.aggregate(pipeline)
                async for doc in cursor:
                    doc.pop('_id', None)  # Remove MongoDB _id
                    combined_results.append(doc)
            except Exception as vector_error:
                print(f"Vector search not available, falling back to text search: {vector_error}")
                # Fallback to text-based search
                cursor = collection.find({
                    "college_name": college_name,
                    "chunk_type": {"$in": ["class", "prerequisite"]},
                    "$text": {"$search": input_text}
                }).limit(50)
                
                async for doc in cursor:
                    doc["similarity"] = 0.5  # Default similarity for text search
                    doc.pop('_id', None)  # Remove MongoDB _id
                    combined_results.append(doc)
            
            return combined_results
            
        except Exception as e:
            print(f"Error getting general chunks: {e}")
            return []

    async def insert_chunk(self, chunk_data: Dict[str, Any]):
        """Insert a new chunk into the vector store"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            result = await collection.insert_one(chunk_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting chunk: {e}")
            return None

    async def update_chunk(self, chunk_id: str, update_data: Dict[str, Any]):
        """Update an existing chunk in the vector store"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            result = await collection.update_one(
                {"id": chunk_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating chunk: {e}")
            return False

    async def delete_chunk(self, chunk_id: str):
        """Delete a chunk from the vector store"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            result = await collection.delete_one({"id": chunk_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting chunk: {e}")
            return False

    async def get_chunk_by_id(self, chunk_id: str):
        """Get a specific chunk by ID"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            doc = await collection.find_one({"id": chunk_id})
            if doc:
                doc.pop('_id', None)  # Remove MongoDB _id
                return doc
            return None
        except Exception as e:
            print(f"Error getting chunk by ID: {e}")
            return None

    async def search_chunks_by_content(self, search_term: str, chunk_type: str = None, college_name: str = None):
        """Search chunks by content using text search"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            # Build query
            query = {"$text": {"$search": search_term}}
            
            if chunk_type:
                query["chunk_type"] = chunk_type
            if college_name:
                query["college_name"] = college_name
            
            cursor = collection.find(query).limit(50)
            
            results = []
            async for doc in cursor:
                doc.pop('_id', None)  # Remove MongoDB _id
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"Error searching chunks by content: {e}")
            return []

    async def get_chunks_by_filter(self, filters: Dict[str, Any], limit: int = 100):
        """Get chunks based on custom filters"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            cursor = collection.find(filters).limit(limit)
            
            results = []
            async for doc in cursor:
                doc.pop('_id', None)  # Remove MongoDB _id
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"Error getting chunks by filter: {e}")
            return []

    def close_connection(self):
        """Close the MongoDB connection"""
        self.mongo.close_connection()