from app.db.connection.mongo_connection import MongoDB
from typing import List, Dict, Any, Optional


class PrerequisiteService:
    def __init__(self):
        self.mongo_db = MongoDB()
        self.collection = self.mongo_db.get_collection("pcc_course_prerequisites")


    async def get_all_prerequisites(self, college: str) -> Dict[str, Any]:
        cursor = self.collection.find({"college": college})

        res = {}
        async for course in cursor:
            course_code = course["course_code"]
            res[course_code] = {
                "name": course["name"],
                "units": course["units"],
                "difficulty": course["difficulty"],
                "assessment_allow": course["assessment_allow"],
                "prerequisites": course["prerequisites"],
                "unlocks": course["unlocks"],
                "department": course["department"]
            }
        
        return res


