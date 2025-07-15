from app.db.connection.mongo_connection import MongoDB
from app.schemas.transferPlanRequest import TransferPlanRequest
from typing import Dict, Optional, Any, List
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

async def db_get_university_by_id(university_id: int) -> Optional[str]:
    """Get university details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("universities")
        
        university = await collection.find_one({"id": university_id})
        if university:
            return university.get("university_name")
        return None
    except Exception as e:
        logger.error(f"Error fetching university by ID {university_id}: {e}")
        return None

async def db_get_major_by_id(major_id: int) -> Optional[str]:
    """Get major details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("majors")
        
        major = await collection.find_one({"id": major_id})
        if major:
            return major.get("major_name")
        return None
    except Exception as e:
        logger.error(f"Error fetching major by ID {major_id}: {e}")
        return None

async def db_get_college_by_id(college_id: int) -> Optional[str]:
    """Get college details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("colleges")
        
        college = await collection.find_one({"id": college_id})
        if college:
            return college.get("college_name")
        return None
    except Exception as e:
        logger.error(f"Error fetching college by ID {college_id}: {e}")
        return None

async def db_get_university_details_by_id(university_id: int) -> Optional[Dict[str, Any]]:
    """Get complete university details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("universities")
        
        university = await collection.find_one({"id": university_id})
        if university:
            # Remove MongoDB's _id field for cleaner response
            university.pop('_id', None)
            return university
        return None
    except Exception as e:
        logger.error(f"Error fetching university details by ID {university_id}: {e}")
        return None

async def db_get_major_details_by_id(major_id: int) -> Optional[Dict[str, Any]]:
    """Get complete major details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("majors")
        
        major = await collection.find_one({"id": major_id})
        if major:
            # Remove MongoDB's _id field for cleaner response
            major.pop('_id', None)
            return major
        return None
    except Exception as e:
        logger.error(f"Error fetching major details by ID {major_id}: {e}")
        return None

async def db_get_college_details_by_id(college_id: int) -> Optional[Dict[str, Any]]:
    """Get complete college details by ID."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("colleges")
        
        college = await collection.find_one({"id": college_id})
        if college:
            # Remove MongoDB's _id field for cleaner response
            college.pop('_id', None)
            return college
        return None
    except Exception as e:
        logger.error(f"Error fetching college details by ID {college_id}: {e}")
        return None

async def db_get_basic_info(request: TransferPlanRequest) -> Dict[str, Any]:
    """Get basic information for college, university, and major."""
    try:
        # Fetch all data concurrently
        college = await db_get_college_by_id(request.college_id)
        university = await db_get_university_by_id(request.university_id)
        major = await db_get_major_by_id(request.major_id)

        if not college or not university or not major:
            logger.error(f"College: {college}")
            logger.error(f"University: {university}")
            logger.error(f"Major: {major}")
            raise ValueError("One or more required entities not found")
            
        return {
            "college": college,
            "university": university,
            "major": major
        }
    except Exception as e:
        logger.error(f"Error getting basic info: {e}")
        raise

async def db_get_detailed_info(request: TransferPlanRequest) -> Dict[str, Any]:
    """Get detailed information for college, university, and major."""
    try:
        # Fetch all detailed data concurrently
        college_details = await db_get_college_details_by_id(request.college_id)
        university_details = await db_get_university_details_by_id(request.university_id)
        major_details = await db_get_major_details_by_id(request.major_id)

        if not college_details or not university_details or not major_details:
            logger.error(f"College details: {college_details}")
            logger.error(f"University details: {university_details}")
            logger.error(f"Major details: {major_details}")
            raise ValueError("One or more required entities not found")
            
        return {
            "college": college_details,
            "university": university_details,
            "major": major_details
        }
    except Exception as e:
        logger.error(f"Error getting detailed info: {e}")
        raise

async def db_get_all_colleges() -> List[Dict[str, Any]]:
    """Get all colleges."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("colleges")
        
        colleges = []
        async for college in collection.find({}):
            college.pop('_id', None)  # Remove MongoDB's _id field
            colleges.append(college)
        
        return colleges
    except Exception as e:
        logger.error(f"Error fetching all colleges: {e}")
        return []

async def db_get_all_universities() -> List[Dict[str, Any]]:
    """Get all universities."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("universities")
        
        universities = []
        async for university in collection.find({}):
            university.pop('_id', None)  # Remove MongoDB's _id field
            universities.append(university)
        
        return universities
    except Exception as e:
        logger.error(f"Error fetching all universities: {e}")
        return []

async def db_get_all_majors() -> List[Dict[str, Any]]:
    """Get all majors."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("majors")
        
        majors = []
        async for major in collection.find({}):
            major.pop('_id', None)  # Remove MongoDB's _id field
            majors.append(major)
        
        return majors
    except Exception as e:
        logger.error(f"Error fetching all majors: {e}")
        return []

async def db_get_uc_universities() -> List[Dict[str, Any]]:
    """Get all UC universities."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("universities")
        
        universities = []
        async for university in collection.find({"is_uc": True}):
            university.pop('_id', None)  # Remove MongoDB's _id field
            universities.append(university)
        
        return universities
    except Exception as e:
        logger.error(f"Error fetching UC universities: {e}")
        return []

async def db_search_colleges_by_name(search_term: str) -> List[Dict[str, Any]]:
    """Search colleges by name."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("colleges")
        
        # Case-insensitive search using regex
        colleges = []
        async for college in collection.find({
            "college_name": {"$regex": search_term, "$options": "i"}
        }):
            college.pop('_id', None)  # Remove MongoDB's _id field
            colleges.append(college)
        
        return colleges
    except Exception as e:
        logger.error(f"Error searching colleges by name '{search_term}': {e}")
        return []

async def db_search_universities_by_name(search_term: str) -> List[Dict[str, Any]]:
    """Search universities by name."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("universities")
        
        # Case-insensitive search using regex
        universities = []
        async for university in collection.find({
            "university_name": {"$regex": search_term, "$options": "i"}
        }):
            university.pop('_id', None)  # Remove MongoDB's _id field
            universities.append(university)
        
        return universities
    except Exception as e:
        logger.error(f"Error searching universities by name '{search_term}': {e}")
        return []

async def db_search_majors_by_name(search_term: str) -> List[Dict[str, Any]]:
    """Search majors by name."""
    try:
        mongo = MongoDB("main_db")
        collection = mongo.get_collection("majors")
        
        # Case-insensitive search using regex
        majors = []
        async for major in collection.find({
            "major_name": {"$regex": search_term, "$options": "i"}
        }):
            major.pop('_id', None)  # Remove MongoDB's _id field
            majors.append(major)
        
        return majors
    except Exception as e:
        logger.error(f"Error searching majors by name '{search_term}': {e}")
        return []