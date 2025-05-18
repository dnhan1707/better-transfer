from sqlalchemy.orm import Session
from app.db.crud.articulations import (
    db_get_articulation_groups,
    db_get_university_by_id,
    db_get_major_by_id,
    db_get_college_by_id,
    db_get_university_courses,
    db_get_course_articulations,
    db_get_cc_courses_with_relationships
)


def get_articulation_groups(
    db: Session,
    college_id: int,
    university_id: int,
    major_id: int
):
    # Use the imported function with different name
    articulation_groups = db_get_articulation_groups(db, college_id, university_id, major_id)
    result = []
    for group in articulation_groups:
        result.append({
            "id": group.id,
            "university_id": group.university_id,
            "major_id": group.major_id,
            "college_id": group.college_id,
            "expression": group.expression
        })
    
    return result

def get_university_name(db: Session, university_id: int):
    university = db_get_university_by_id(db, university_id)
    return university.university_name

def get_major_name(db: Session, major_id: int):
    major = db_get_major_by_id(db, major_id)
    return major.major_name

def get_college_name(db: Session, college_id: int):
    college = db_get_college_by_id(db, college_id)
    return college.college_name

def simplified_articulation_group(    
    db: Session,
    college_id: int,
    university_id: int,
    major_id: int
): 
    try:
        # Get basic information
        result = db_get_articulation_groups(db, college_id, university_id, major_id)
        
        # Check what db_get_articulation_groups returns
        if isinstance(result, tuple) and len(result) == 2:
            # It returns (articulation_groups, course_codes)
            articulation_groups, uni_course_codes = result
        else:
            # It returns just articulation_groups
            articulation_groups = result
        
        # Create result structure
        college_uni_agreement = {
            "university": get_university_name(db, university_id),
            "major": get_major_name(db, major_id),
            "college": get_college_name(db, college_id),
            "requirementTree": None
        }
        
        # Get course mappings with relationship types
        cc_course_mappings = db_get_cc_courses_with_relationships(db, university_id, college_id)
        
        # Build a dictionary for easier lookup when processing expressions
        course_mappings = {}
        for mapping in cc_course_mappings:
            uni_course = mapping["university_course"]
            
            # Store both relationship type and courses
            course_mappings[uni_course] = {
                "relationship_type": mapping["relationship_type"],
                "courses": [course["code"] for course in mapping["community_college_courses"]]
            }
        
        # Process the articulation groups to build the requirement tree
        if articulation_groups and len(articulation_groups) > 0:
            # Take the first group's expression as the root
            main_group = articulation_groups[0]
            college_uni_agreement["requirementTree"] = process_expression(main_group.expression, course_mappings)
        
        return college_uni_agreement
    except Exception as e:
        print(f"Error generating simplified articulation group: {str(e)}")
        # Include traceback for better debugging
        import traceback
        traceback.print_exc()
        raise

def process_expression(expression, course_mappings):
    """
    Recursively process an expression to build a requirement tree
    
    Args:
        expression: A dict with operator and groups fields
        course_mappings: Dictionary mapping university course codes to relationship and courses
    """
    if not expression:
        return None
        
    operator = expression.get("operator", "AND")
    groups = expression.get("groups", [])
    
    processed_groups = []
    for group in groups:
        if isinstance(group, dict) and "operator" in group:
            # This is a nested expression
            processed_groups.append(process_expression(group, course_mappings))
        else:
            # This is a university course code
            uni_course_code = group
            
            # Get relationship type and courses
            mapping = course_mappings.get(uni_course_code, {"relationship_type": "OR", "courses": []})
            relationship_type = mapping["relationship_type"]
            cc_courses = mapping["courses"]
            
            processed_groups.append({
                "university_course": uni_course_code,
                "cc_course_relationship": relationship_type,  # Include relationship type
                "community_college_courses": cc_courses
            })
    
    return {
        "operator": operator,
        "groups": processed_groups
    }

def evaluate_student_articulation_progress(
    student_completed_courses,  # List of course codes the student has completed
    articulation_tree           # The requirement tree returned by simplified_articulation_group
):
    """
    Evaluates whether a student has satisfied the articulation requirements
    
    Returns:
        dict with status and details about which requirements are met/unmet
    """
    def evaluate_node(node):
        if "university_course" in node:
            # This is a leaf node (university course)
            required_courses = node["community_college_courses"]
            relationship = node["cc_course_relationship"]
            
            if relationship == "AND":
                # Must have taken ALL courses
                satisfied = all(course in student_completed_courses for course in required_courses)
            else:
                # Must have taken at least ONE course
                satisfied = any(course in student_completed_courses for course in required_courses)
                
            return {
                "satisfied": satisfied,
                "university_course": node["university_course"],
                "completed_courses": [c for c in required_courses if c in student_completed_courses],
                "missing_courses": [c for c in required_courses if c not in student_completed_courses]
            }
        else:
            # This is an operator node (AND/OR)
            child_results = [evaluate_node(child) for child in node["groups"]]
            
            if node["operator"] == "AND":
                satisfied = all(result["satisfied"] for result in child_results)
            else:
                satisfied = any(result["satisfied"] for result in child_results)
                
            return {
                "satisfied": satisfied,
                "operator": node["operator"],
                "requirements": child_results
            }
    
    return evaluate_node(articulation_tree)