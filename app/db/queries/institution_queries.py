from sqlalchemy.orm import Session
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.colleges import Colleges
from app.schemas.transferPlanRequest import TransferPlanRequest
from typing import Dict, Optional, Any
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def db_get_university_by_id(db: Session, university_id: int) -> Optional[Universities]:
    """Get university details by ID."""
    return db.query(Universities).filter(
        Universities.id == university_id
    ).first()

def db_get_major_by_id(db: Session, major_id: int) -> Optional[Majors]:
    """Get major details by ID."""
    return db.query(Majors).filter(
        Majors.id == major_id
    ).first()

def db_get_college_by_id(db: Session, college_id: int) -> Optional[Colleges]:
    """Get college details by ID."""
    return db.query(Colleges).filter(
        Colleges.id == college_id
    ).first()


def db_get_basic_info(db: Session, request: TransferPlanRequest) -> Dict[str, Any]:
    try:
        college = db_get_college_by_id(db, request.college_id)
        university = db_get_university_by_id(db, request.university_id)
        major = db_get_major_by_id(db, request.major_id)
        if(not college or not university or not major):
            logger.error(f"College: {college}")
            logger.error(f"University: {university}")
            logger.error(f"Major: {major}")
            raise Exception
            
        return {
            "college": college,
            "university": university,
            "major": major
        }
    except Exception:
        logger.error("Info not found")


