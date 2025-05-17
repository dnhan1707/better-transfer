from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.articulation_group import ArticulationGroup
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
            ArticulationGroup,
            UniversityCourses,
            Courses, 
        )
        .join(
            UniversityCourses,
            UniversityCourses.id == func.any(ArticulationGroup.university_course_ids)
        )
        .filter(
            Courses.college_id == college_id,
            ArticulationGroup.university_id == university_id,
            ArticulationGroup.major_id == major_id
        )
        .all()
    )
    
    return articulations