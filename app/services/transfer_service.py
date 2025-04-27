from sqlalchemy.orm import Session
from app.db.crud.articulations import get_required_cc_courses_for_transfer


def generate_transfer_plan(
    db: Session,
    college_id: int,
    university_id: int,
    major_id: int
):
    articulations = get_required_cc_courses_for_transfer(db, college_id, university_id, major_id)
    result = {}
    for university_course, cc_course in articulations:
        # Use university course ID as key
        uni_course_id = university_course.id
        
        if uni_course_id not in result:
            # Store university course info alongside the list
            result[uni_course_id] = {
                "university_course": {
                    "id": university_course.id,
                    "course_code": university_course.course_code,
                    "course_name": university_course.course_name
                },
                "articulated_courses": []
            }
        
        # Add community college course as a dictionary
        result[uni_course_id]["articulated_courses"].append({
            "id": cc_course.id,
            "code": cc_course.code,
            "name": cc_course.name,
            "units": cc_course.units,
            "difficulty": cc_course.difficulty
        })
    
    return result
