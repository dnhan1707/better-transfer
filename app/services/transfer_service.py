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
    for articulation_group, uni_course, cc_course, group_course in articulations:
        # Use university course ID as key
        uni_course_id = uni_course.id
        
        if uni_course_id not in result:
            # Store university course info alongside the list
            result[uni_course_id] = {
                "university_course": {
                    "id": uni_course_id,
                    "course_code": uni_course.course_code,
                    "course_name": uni_course.course_name
                },
                "articulated_group" : {}
            }
        
        group_id = articulation_group.id
        if group_id not in result[uni_course_id]["articulation_groups"]:
            result[uni_course_id]["articulation_groups"][group_id] = {
                "operator": articulation_group.operator.value,
                "courses": []
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
