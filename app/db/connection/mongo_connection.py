import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _instances = {}
    
    def __new__(cls, database_name: str = None):
        # Use default database if none specified
        if database_name is None:
            database_name = "course_prerequisite"
            
        if database_name not in cls._instances:
            instance = super(MongoDB, cls).__new__(cls)
            connection_url = os.getenv("MONGO_DB_PCC_CLUSTER_CONNECTION_URL")
            instance._client = AsyncIOMotorClient(connection_url)
            instance._db = instance._client.get_database(database_name)
            instance._database_name = database_name
            cls._instances[database_name] = instance
        
        return cls._instances[database_name]

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
            # Remove from instances when closed
            if self._database_name in self._instances:
                del self._instances[self._database_name]

    @classmethod
    def close_all_connections(cls):
        """Close all MongoDB connections"""
        for instance in cls._instances.values():
            instance.close_connection()
        cls._instances.clear()