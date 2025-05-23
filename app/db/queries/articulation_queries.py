from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.articulation_group import ArticulationGroup
from app.db.models.courses import Courses
from app.db.models.university_courses import UniversityCourses

def db_get_articulation_groups(db: Session, college_id: int, university_id: int, major_id: int):
    """
    Returns all articulation groups for a specific college-university-major combination
    with additional metadata
    """
    try:
        articulation_groups = (
            db.query(ArticulationGroup)
            .filter(
                ArticulationGroup.college_id == college_id,
                ArticulationGroup.university_id == university_id,
                ArticulationGroup.major_id == major_id
            )
            .all()
        )
        
        # Collect all university course codes from expressions
        all_uni_course_codes = set()
        for group in articulation_groups:
            # Extract course codes from nested expressions
            def extract_course_codes(expr):
                codes = []
                if isinstance(expr, dict):
                    groups = expr.get("groups", [])
                    for g in groups:
                        if isinstance(g, str):  # It's a course code
                            codes.append(g)
                        elif isinstance(g, dict):  # It's a nested expression
                            codes.extend(extract_course_codes(g))
                return codes
            
            # Get course codes from this group's expression
            course_codes = extract_course_codes(group.expression)
            all_uni_course_codes.update(course_codes)
        
        return articulation_groups, list(all_uni_course_codes)
    except Exception as e:
        print(f"Error retrieving articulation groups: {str(e)}")
        raise

def db_get_articulation_group_filtered(db: Session, college_id: int, university_id: int, major_id: int):
    """Get filtered articulation groups."""
    return db.query(ArticulationGroup).filter(
        ArticulationGroup.university_id == university_id,
        ArticulationGroup.major_id == major_id,
        ArticulationGroup.college_id == college_id
    ).all()

def db_get_course_articulations(db: Session, college_id: int, university_id: int):
    """Get all course articulations between a college and university."""
    return db.query(
        ArticulationAgreements,
        UniversityCourses,
        Courses
    ).join(
        UniversityCourses,
        ArticulationAgreements.university_course_id == UniversityCourses.id
    ).join(
        Courses,
        ArticulationAgreements.community_college_course_id == Courses.id
    ).filter(
        Courses.college_id == college_id,
        UniversityCourses.university_id == university_id
    ).all()

def db_get_cc_courses_for_uni_course(db: Session, university_course_id: int, college_id: int):
    """Get all community college courses that articulate to a university course."""
    return db.query(Courses).join(
        ArticulationAgreements,
        ArticulationAgreements.community_college_course_id == Courses.id
    ).filter(
        ArticulationAgreements.university_course_id == university_course_id,
        Courses.college_id == college_id
    ).all()

def db_get_cc_courses_with_relationships(db: Session, university_id: int, college_id: int):
    """Get community college courses grouped by university course with relationship types."""
    try:
        # Get all articulations
        articulations = db.query(
            ArticulationAgreements,
            UniversityCourses,
            Courses
        ).join(
            UniversityCourses,
            ArticulationAgreements.university_course_id == UniversityCourses.id
        ).join(
            Courses,
            ArticulationAgreements.community_college_course_id == Courses.id
        ).filter(
            Courses.college_id == college_id,
            UniversityCourses.university_id == university_id
        ).all()
        
        # Group by university course and group_id
        result = {}
        for agreement, uni_course, cc_course in articulations:
            key = (uni_course.id, agreement.group_id)
            
            if key not in result:
                result[key] = {
                    "university_course": uni_course.course_code,
                    "relationship_type": agreement.relationship_type.value,
                    "community_college_courses": []
                }
                
            result[key]["community_college_courses"].append({
                "code": cc_course.code,
                "name": cc_course.name
            })
        
        # Return as a list of course groups
        return list(result.values())
    except Exception as e:
        print(f"Error retrieving CC courses with relationships: {str(e)}")
        raise

def db_get_cc_course_relationships_for_expression(db: Session, university_id: int, college_id: int, university_course_codes: list):
    """
    Get relationships between community college courses for specific university courses.
    """
    # Filter to only include the courses we need for this expression
    articulations = db.query(
        ArticulationAgreements,
        UniversityCourses,
        Courses
    ).join(
        UniversityCourses,
        ArticulationAgreements.university_course_id == UniversityCourses.id
    ).join(
        Courses,
        ArticulationAgreements.community_college_course_id == Courses.id
    ).filter(
        Courses.college_id == college_id,
        UniversityCourses.university_id == university_id,
        UniversityCourses.course_code.in_(university_course_codes)
    ).all()
    
    # Group by university course code and group_id
    result = {}
    for agreement, uni_course, cc_course in articulations:
        # Use course code as key for easier lookup in the expression processor
        if uni_course.course_code not in result:
            result[uni_course.course_code] = {
                "relationship_type": agreement.relationship_type.value,
                "community_college_courses": []
            }
            
        # Add the community college course
        result[uni_course.course_code]["community_college_courses"].append({
            "code": cc_course.code,
            "name": cc_course.name
        })
    
    return result