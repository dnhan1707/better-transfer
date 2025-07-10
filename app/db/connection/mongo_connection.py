import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            connection_url = os.getenv("MONGO_DB_PCC_CLUSTER_CONNECTION_URL")
            cls._client = AsyncIOMotorClient(connection_url)
            cls._db = cls._client.get_database("course_prerequisite")
        return cls._instance

    def get_db(self):
        """Get MongoDB database instance"""
        return self._db

    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self._db[collection_name]

    def close_connection(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()