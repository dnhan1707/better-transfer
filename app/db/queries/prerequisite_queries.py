from sqlalchemy.orm import Session, aliased
from app.db.models.prerequisites import Prerequisites
from app.db.models.courses import Courses

def db_get_prerequisite_relationships_for_college(db: Session, college_id: int):
    """Get all prerequisite relationships for courses at a college."""
    PrerequisiteCourse = aliased(Courses)
    return db.query(
        Courses.code.label("course_code"),
        Prerequisites.prerequisite_type,
        PrerequisiteCourse.code.label("prerequisite_code")
    ).join(
        Prerequisites,
        Courses.id == Prerequisites.course_id
    ).join(
        PrerequisiteCourse,
        Prerequisites.prerequisite_course_id == PrerequisiteCourse.id
    ).filter(
        Courses.college_id == college_id
    ).all()

def db_get_course_prerequisites(db: Session, course_id: int):
    """Get all prerequisites for a specific course."""
    PrerequisiteCourse = aliased(Courses)
    return db.query(
        Prerequisites.prerequisite_type,
        PrerequisiteCourse
    ).join(
        PrerequisiteCourse,
        Prerequisites.prerequisite_course_id == PrerequisiteCourse.id
    ).filter(
        Prerequisites.course_id == course_id
    ).all()