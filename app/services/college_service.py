from app.db.connection.mongo_connection import MongoDB
from app.schemas.transferPlanRequest import InputRequest
from app.utils.logging_config import get_logger
from bson.objectid import ObjectId

logger = get_logger(__name__)

class CollegeService():
    def __init__(self):
        self.mongo = MongoDB("main_db")
        self.collection = self.mongo.get_collection("colleges")

        
    async def get_college_code(self, college_id: str):
        try:
            college = await self.collection.find_one({"_id": ObjectId(college_id)})
            
            # Check if college exists
            if not college:
                logger.warning(f"College not found with id: {college_id}")
                return None
            if "code" not in college:
                logger.warning(f"College {college_id} missing 'code' field. Available fields: {list(college.keys())}")
                return None
            
            college_code = college["code"]
            return college_code

        except Exception as e:
            logger.error(f"Error fetching college: {e}")  
            raise
    
    
