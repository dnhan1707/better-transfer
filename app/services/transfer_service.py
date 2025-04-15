from sqlalchemy.orm import Session
from app.db.crud.articulations import get_required_cc_courses_for_transfer
from app.schemas.transfer import TransferPlanCourse


def generate_transfer_plan(
    db: Session,
    college_id: int,
    university_id: int,
    major_id: int
) -> list[TransferPlanCourse]:
    cc_courses = get_required_cc_courses_for_transfer(db, college_id, university_id, major_id)

    result = []

    for course in cc_courses:
        result.append(
            TransferPlanCourse(           
                course_id=course.id,
                code=course.code,
                name=course.name,
                units=course.units,
                difficulty=course.difficulty
            )
        )
    
    return result
