from app.db.connection.mongo_connection import MongoDB
from typing import Dict, Any
from app.utils.logging_config import get_logger
from bson.objectid import ObjectId

logger = get_logger(__name__)

class PrerequisiteService:
    def __init__(self):
        self.mongo_db = MongoDB("course_prerequisite")
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

class CollegeUniMajorPairService:
    def __init__(self):
        self.mongo_db = MongoDB("main_db")
        self.collection = self.mongo_db.get_collection("college_uni_major_pair")

    async def get_majors_with_names(self, university_id: str, college_id: str):
        """Get majors with names using aggregation pipeline"""
        try:
            uni_object_id = ObjectId(university_id)
            college_object_id = ObjectId(college_id)

            pipeline = [
                {
                    "$match": {
                        "to_university_id": uni_object_id,
                        "from_college_id": college_object_id,
                        "is_active": True
                    }
                },
                {
                    "$lookup": {
                        "from": "majors",  
                        "localField": "major_id",
                        "foreignField": "_id",
                        "as": "major_details"
                    }
                },
                {
                    "$lookup": {
                        "from": "majors",
                        "localField": "alter_major_id", 
                        "foreignField": "_id",
                        "as": "alter_major_details"
                    }
                },
                {
                    "$project": {
                        "_id": 0,  
                        "major_id": {"$toString": "$major_id"},
                        "major_name": {
                            "$cond": {
                                "if": {"$gt": [{"$size": "$major_details"}, 0]},
                                "then": {"$arrayElemAt": ["$major_details.major_name", 0]},
                                "else": "Unknown Major"
                            }
                        },
                        "alter_major_id": {
                            "$cond": {
                                "if": {"$and": [
                                    {"$ne": ["$alter_major_id", None]},
                                    {"$ne": ["$alter_major_id", None]}
                                ]},
                                "then": {"$toString": "$alter_major_id"},
                                "else": None  
                            }
                        },
                        "alter_major_name": {
                            "$cond": {
                                "if": {"$gt": [{"$size": "$alter_major_details"}, 0]},
                                "then": {"$arrayElemAt": ["$alter_major_details.major_name", 0]},
                                "else": None  
                            }
                        }
                    }
                },
                {
                    "$sort": {"major_name": 1}
                }
            ]

            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(None)
            
            logger.info(f"Aggregation with names returned {len(results)} results")
            
            safe_results = []
            for result in results:
                safe_result = {}
                for key, value in result.items():
                    if isinstance(value, ObjectId):
                        safe_result[key] = str(value)
                    else:
                        safe_result[key] = value
                safe_results.append(safe_result)
            
            return safe_results

        except Exception as e:
            logger.error(f"Error get_majors_with_names: {e}")
            raise
class MajorService:
    def __init__(self):
        self.mongo_db = MongoDB("main_db")
        self.collection = self.mongo_db.get_collection("major")

    async def get_major_by_id(self, id: ObjectId):
        try:
            doc = await self.collection.find_one({"_id": id})
            if not doc:
                logger.warning(f"No major found with id: {id}")
                return None

            return {
                "major_id": str(doc["_id"]),  
                "major_name": doc["major_name"]
            }

        except Exception as e:
            logger.error(f"Error get_major_by_id: {e}")
            raise


class InstitutionService:
    def __init__(self):
        self.mongo_db = MongoDB("main_db")
        self.uni_collection = self.mongo_db.get_collection("universities")
        self.college_collection = self.mongo_db.get_collection("colleges")

    async def get_institutions_by_type(self, institution_type: str):
        """Get institutions by type (university or college)"""
        try:
            # Fix: Check for singular forms to match API calls
            if institution_type == "university":
                return await self.get_all_universities()
            elif institution_type == "college":
                return await self.get_all_colleges()
            else:
                raise ValueError(f"Invalid institution type: {institution_type}")
            
        except Exception as e:
            logger.error(f"Error getting {institution_type}s: {e}")
            raise

    async def get_all_universities(self):
        try:
            universities_list = []
            cursor = self.uni_collection.find({})
            async for university in cursor:
                universities_list.append({
                    "id": str(university["_id"]),
                    "university_name": university.get("university_name", ""),
                    "type": "university"
                })

            return universities_list

        except Exception as e:
            # Fix: Correct error message
            logger.error(f"Error getting all universities: {e}")
            raise

    async def get_all_colleges(self):
        try:
            colleges_list = []
            cursor = self.college_collection.find({})
            async for college in cursor:
                colleges_list.append({
                    "id": str(college["_id"]),
                    "college_name": college.get("college_name", ""),
                    "type": "college"
                })

            return colleges_list

        except Exception as e:
            # Fix: Correct error message
            logger.error(f"Error getting all colleges: {e}")
            raise

    # Add missing method
    async def get_all_institutions(self):
        """Get all institutions (universities and colleges combined)"""
        try:
            universities = await self.get_all_universities()
            colleges = await self.get_all_colleges()
            
            return {
                "universities": universities,
                "colleges": colleges,
                "total_universities": len(universities),
                "total_colleges": len(colleges),
                "total_count": len(universities) + len(colleges)
            }
            
        except Exception as e:
            logger.error(f"Error getting all institutions: {e}")
            raise
