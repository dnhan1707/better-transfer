from sqlalchemy.orm import Session
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.colleges import Colleges

def db_get_university_by_id(db: Session, university_id: int):
    """Get university details by ID."""
    return db.query(Universities).filter(
        Universities.id == university_id
    ).first()

def db_get_major_by_id(db: Session, major_id: int):
    """Get major details by ID."""
    return db.query(Majors).filter(
        Majors.id == major_id
    ).first()

def db_get_college_by_id(db: Session, college_id: int):
    """Get college details by ID."""
    return db.query(Colleges).filter(
        Colleges.id == college_id
    ).first()