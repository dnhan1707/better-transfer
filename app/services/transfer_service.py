from sqlalchemy.orm import Session
from app.db.crud.articulations import (
    db_get_articulation_groups,
    db_get_university_by_id,
    db_get_major_by_id,
    db_get_college_by_id,
    db_get_university_courses,
    db_get_course_articulations,
    db_get_cc_courses_with_relationships,
    db_get_cc_courses_for_uni_course
)
from app.services.prerequisite_graph import build_prerequisite_graph
from app.db.models.courses import Courses
from app.db.models.articulation_group import ArticulationGroup
from app.db.models.expression_node import NodeType
from app.services.prerequisite_graph import topological_sort, plan_course_sequence



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
            if len(articulation_groups) == 1:
                # Just one group, use it directly
                main_group = articulation_groups[0]
                college_uni_agreement["requirementTree"] = process_expression(main_group.expression, course_mappings)
            else:
                # Multiple groups - combine them into a single AND expression
                combined_expression = {
                    "operator": "AND",
                    "groups": [group.expression for group in articulation_groups]
                }
                college_uni_agreement["requirementTree"] = process_expression(combined_expression, course_mappings)
        
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


def process_expression_tree(db, node, uni_to_cc_map, cc_to_uni_map):
    if node.node_type == NodeType.COURSE:
        if node.university_course:
            uni_course_code = node.university_course.course_code
            # Get all CC courses that articulate to this university course
            cc_courses = db_get_cc_courses_for_uni_course(
                db, 
                node.university_course.id, 
                node.articulation_group.college_id
            )

            # Map university course -> CC courses (FIX HERE)
            if uni_course_code not in uni_to_cc_map:
                uni_to_cc_map[uni_course_code] = []
            for course in cc_courses:
                if course.code not in uni_to_cc_map[uni_course_code]:
                    uni_to_cc_map[uni_course_code].append(course.code)

            # Map CC courses -> university course
            for cc_course in cc_courses:
                if cc_course.code not in cc_to_uni_map:
                    cc_to_uni_map[cc_course.code] = []
                if uni_course_code not in cc_to_uni_map[cc_course.code]:
                    cc_to_uni_map[cc_course.code].append(uni_course_code)
            
    elif node.node_type == NodeType.OPERATOR:
        for child in node.child_nodes:
            process_expression_tree(db, child, uni_to_cc_map, cc_to_uni_map)

def create_transfer_plan(db: Session, college_id: int, university_id: int, major_id: int, num_of_terms: int):
    # Get basic information
    college = db_get_college_by_id(db, college_id)
    university = db_get_university_by_id(db, university_id)
    major = db_get_major_by_id(db, major_id)
    
    articulation_groups = db.query(ArticulationGroup).filter(
        ArticulationGroup.university_id == university_id,
        ArticulationGroup.major_id == major_id,
        ArticulationGroup.college_id == college_id
    ).all()

    if not articulation_groups:
        return {"error": "No articulation agreements found for this combination"}
    
    uni_to_cc_map = {}  # Maps university courses to CC courses
    '''
    it looks like this:
    uni_to_cc_map = {
        "COM SCI 31": ["CS 003A", "CIS 014"],
        "COM SCI 32": ["CS 008"],
        "MATH 31A": ["MATH 005A"]
    }
    '''
    cc_to_uni_map = {}  # Maps CC courses to university courses they satisfy
    
    for group in articulation_groups:
        # Start from the root node of each articulation group
        if group.root_node:
            process_expression_tree(db, group.root_node, uni_to_cc_map, cc_to_uni_map)

    cc_courses_to_take = set()
    for cc_list in uni_to_cc_map.values():
        for cc in cc_list:
            cc_courses_to_take.add(cc)
    '''
    it should looks like this: {"CS 003A", "CIS 014", "CS 008", "MATH 005A"}
    '''
    courses = db.query(Courses).filter(
        Courses.college_id == college_id,
        Courses.code.in_(cc_courses_to_take)
    ).all()

    course_details = {}
    for course in courses:
        course_details[course.code] = {
            "units": course.units,
            "name": course.name
        } 
    
    prerequisite_graph, _ = build_prerequisite_graph(db, college_id)
    sorted_courses = topological_sort(prerequisite_graph)
    sorted_courses = [c for c in sorted_courses if c in cc_courses_to_take]

    term_plan = plan_course_sequence(sorted_courses, num_of_terms, prerequisite_graph)
    print("----------------FIXED TERM PLAN----------------------")
    print(sorted_courses)
    print(term_plan)
    print("-----------------------------------------------------")

    formatted_plan = {
        "university": university.university_name,
        "college": college.college_name,
        "major": major.major_name,
        "term_plan": []
    }
    

    # Track completed courses for prerequisite checking
    completed_courses = set()
    for term_index, term_courses in enumerate(term_plan):
        term_data = {
            "term": term_index + 1,
            "courses": []
        }
        
        for cc_course in term_courses:
            # Skip courses not in our mapping (this shouldn't happen, but just in case)
            if cc_course not in cc_to_uni_map:
                continue
            
            # Get which university course(s) this satisfies
            uni_courses = cc_to_uni_map[cc_course]
            
            # For each university course this CC course satisfies
            for uni_course in uni_courses:
                # Get alternatives (other CC courses that satisfy the same university course)
                alternatives = [c for c in uni_to_cc_map.get(uni_course, []) if c != cc_course]
                
                # Get prerequisites for this course
                prereqs = []
                for prereq in prerequisite_graph.get(cc_course, []):
                    if isinstance(prereq, dict) and "code" in prereq:
                        prereq_code = prereq["code"]
                        if prereq_code in cc_courses_to_take:
                            prereqs.append(prereq_code)
                
                # Create course entry
                course_entry = {
                    "university_course": uni_course,
                    "selected": cc_course,
                    "alternatives": alternatives,
                    "prerequisites": prereqs,
                    "units": course_details.get(cc_course, {}).get("units", 0)
                }
                
                term_data["courses"].append(course_entry)
            
            completed_courses.add(cc_course)
        
        formatted_plan["term_plan"].append(term_data)
    
    # Handle multiple entries for the same university course (keep only one per term)
    consolidate_university_courses(formatted_plan)
    
    return formatted_plan

def consolidate_university_courses(plan):
    """
    Ensure each university course appears only once in each term
    by removing duplicates.
    """
    for term_data in plan["term_plan"]:
        seen_uni_courses = set()
        filtered_courses = []
        
        for course in term_data["courses"]:
            if course["university_course"] not in seen_uni_courses:
                seen_uni_courses.add(course["university_course"])
                filtered_courses.append(course)
        
        term_data["courses"] = filtered_courses
