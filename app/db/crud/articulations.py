from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.courses import Courses
from app.db.models.university_courses import UniversityCourses
from sqlalchemy import func

def get_required_cc_courses_for_transfer(db: Session, college_id: int, university_id: int, major_id: int):
    """
    Returns a dictionary where:
    - Keys are university course IDs
    - Values are lists of community college courses that articulate to that university course
    """
    articulations = (
        db.query(
            UniversityCourses,
            Courses
        )
        .join(
            ArticulationAgreements,
            UniversityCourses.id == ArticulationAgreements.university_course_id
        )
        .join(
            Courses,
            Courses.id == ArticulationAgreements.community_college_course_id
        )
        .filter(
            Courses.college_id == college_id,
            ArticulationAgreements.university_id == university_id,
            ArticulationAgreements.major_id == major_id
        )
        .all()
    )
    
    return articulations