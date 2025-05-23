from sqlalchemy.orm import Session
from app.db.models.university_courses import UniversityCourses
from app.db.models.courses import Courses

def db_get_university_courses(db: Session, university_id: int):
    """Get all courses offered by a university."""
    return db.query(UniversityCourses).filter(
        UniversityCourses.university_id == university_id
    ).all()

def db_get_university_course_by_code(db: Session, university_id: int, course_code: str):
    """Get a university course by its code."""
    return db.query(UniversityCourses).filter(
        UniversityCourses.university_id == university_id,
        UniversityCourses.course_code == course_code
    ).first()

def db_get_college_courses(db: Session, college_id: int):
    """Get all courses offered by a community college."""
    return db.query(Courses).filter(
        Courses.college_id == college_id
    ).all()