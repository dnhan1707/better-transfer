from app.db.connection.mongo_connection import MongoDB
from typing import Optional, List
import hashlib
from datetime import datetime
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class CachingService:
    def __init__(self):
        self.mongo = MongoDB("vector_db")
        self.collection_name = "embedding_cache"

    async def create_cache_indexes(self):
        """Create indexes for the embedding cache collection"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            # Create unique index on content_hash
            await collection.create_index([("content_hash", 1)], unique=True)
            
            # Create index on created_at for potential cleanup operations
            await collection.create_index([("created_at", 1)])
            
            logger.info("Embedding cache indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating cache indexes: {e}")

    async def get_cached_embedding(self, content: str) -> Optional[List[float]]:
        """Get cached embedding for content"""
        try:
            content_hash = self._hash_content(content)
            collection = self.mongo.get_collection(self.collection_name)
            
            doc = await collection.find_one({"content_hash": content_hash})
            
            if doc:
                return doc.get("embedding")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached embedding: {e}")
            return None

    async def cache_embedding(self, content: str, embedding: List[float]):
        """Cache an embedding for content"""
        try:
            content_hash = self._hash_content(content)
            collection = self.mongo.get_collection(self.collection_name)
            
            document = {
                "content_hash": content_hash,
                "content": content,
                "embedding": embedding,
                "created_at": datetime.utcnow()
            }
            
            # Use upsert to avoid duplicates
            await collection.update_one(
                {"content_hash": content_hash},
                {"$set": document},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")

    async def batch_cache_embeddings(self, content_list: List[str], embeddings: List[List[float]]):
        """Cache multiple embeddings at once"""
        try:
            if len(content_list) != len(embeddings):
                raise ValueError("Content list and embeddings list must have the same length")
                
            collection = self.mongo.get_collection(self.collection_name)
            
            documents = []
            for content, embedding in zip(content_list, embeddings):
                content_hash = self._hash_content(content)
                documents.append({
                    "content_hash": content_hash,
                    "content": content,
                    "embedding": embedding,
                    "created_at": datetime.utcnow()
                })
            
            # Use bulk write for better performance
            operations = []
            for doc in documents:
                operations.append({
                    "updateOne": {
                        "filter": {"content_hash": doc["content_hash"]},
                        "update": {"$set": doc},
                        "upsert": True
                    }
                })
            
            if operations:
                await collection.bulk_write(operations)
                logger.info(f"Batch cached {len(operations)} embeddings")
                
        except Exception as e:
            logger.error(f"Error batch caching embeddings: {e}")

    async def get_cache_stats(self):
        """Get statistics about the embedding cache"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            
            total_count = await collection.count_documents({})
            
            # Get size estimation (approximate)
            stats = await collection.aggregate([
                {"$group": {
                    "_id": None,
                    "total_docs": {"$sum": 1},
                    "avg_content_length": {"$avg": {"$strLenCP": "$content"}}
                }}
            ]).to_list(length=1)
            
            result = {
                "total_cached_embeddings": total_count,
                "average_content_length": stats[0]["avg_content_length"] if stats else 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"total_cached_embeddings": 0, "average_content_length": 0}

    async def clear_cache(self):
        """Clear all cached embeddings"""
        try:
            collection = self.mongo.get_collection(self.collection_name)
            result = await collection.delete_many({})
            logger.info(f"Cleared {result.deleted_count} cached embeddings")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    async def remove_old_cache_entries(self, days_old: int = 30):
        """Remove cache entries older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            collection = self.mongo.get_collection(self.collection_name)
            result = await collection.delete_many({"created_at": {"$lt": cutoff_date}})
            
            logger.info(f"Removed {result.deleted_count} old cache entries")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error removing old cache entries: {e}")
            return 0

    def _hash_content(self, content: str) -> str:
        """Create normalized hash of content for lookup"""
        normalized = content.strip().lower()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def close_connection(self):
        """Close the MongoDB connection"""
        self.mongo.close_connection()