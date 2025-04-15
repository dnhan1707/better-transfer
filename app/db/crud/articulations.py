from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.courses import Courses

def get_required_cc_courses_for_transfer(db: Session, college_id: int, university_id: int, major_id: int):
    results = (
        db.query(Courses)
        .join(ArticulationAgreements, Courses.id == ArticulationAgreements.community_college_course_id)
        .filter(
            Courses.college_id == college_id,
            ArticulationAgreements.university_id == university_id,
            ArticulationAgreements.major_id == major_id
        )
        .distinct()
        .all()
    )
    return results
