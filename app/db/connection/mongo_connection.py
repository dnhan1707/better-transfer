import os
from pymongo import MongoClient
from pymongo.database import Database
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
            cls._client = MongoClient(connection_url)
            cls._db = cls._client.get_database("course_prerequisite")

        return cls._instance


    async def get_db(self) -> Database:
        return self._db
    
    async def get_collection(self, collection_name: str):
        return self._db[collection_name]
    
    async def close_connection(self):
        if self._client: 
            self._client.cloas()
    

