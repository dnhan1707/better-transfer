from sqlalchemy.orm import Session
from app.db.queries.institution_queries import (
    db_get_university_by_id,
    db_get_major_by_id,
    db_get_college_by_id
)
from app.db.queries.articulation_queries import db_get_articulation_group_filtered

from app.db.models.courses import Courses
from app.services.prerequisite_service import PrerequisiteService
from app.services.course_scheduling_service import CourseSchedulingService
from app.services.articulation_service import ArticulationService
from app.services.student_progress_service import StudentProgressService
import traceback

class TransferPlanService:
    """Service for generating transfer plans."""
    
    @staticmethod
    def get_basic_info(db: Session, college_id: int, university_id: int, major_id: int):
        """Get basic information about college, university, and major."""
        college = db_get_college_by_id(db, college_id)
        university = db_get_university_by_id(db, university_id)
        major = db_get_major_by_id(db, major_id)
        return {
            "college": college,
            "university": university,
            "major": major
        }
    
    @staticmethod
    def extract_course_details(courses):
        """Extract details like units and name from course objects."""
        course_details = {}
        for course in courses:
            course_details[course.code] = {
                "units": course.units,
                "name": course.name
            } 
        return course_details
    
    @staticmethod
    def get_university_name(db: Session, university_id: int):
        university = db_get_university_by_id(db, university_id)
        return university.university_name

    @staticmethod
    def get_major_name(db: Session, major_id: int):
        major = db_get_major_by_id(db, major_id)
        return major.major_name

    @staticmethod
    def get_college_name(db: Session, college_id: int):
        college = db_get_college_by_id(db, college_id)
        return college.college_name
    
    @staticmethod
    def map_alternatives_cc_classes(uni_to_cc_map):
        uni_course_alternatives = {}
        for uni_course, cc_courses in uni_to_cc_map.items():
            uni_course_alternatives[uni_course] = cc_courses
        
        return uni_course_alternatives

    @staticmethod
    def simplified_articulation_group(db: Session, college_id: int, university_id: int, major_id: int):
        try:
            # Fetch articulation data
            articulation_groups = db_get_articulation_group_filtered(db, college_id, university_id, major_id)
            
            # Build course mappings
            course_mappings = ArticulationService.build_course_mappings(db, university_id, college_id)
            
            # Create result structure
            college_uni_agreement = {
                "university": TransferPlanService.get_university_name(db, university_id),
                "major": TransferPlanService.get_major_name(db, major_id),
                "college": TransferPlanService.get_college_name(db, college_id),
                "requirementTree": ArticulationService.build_requirement_tree(articulation_groups, course_mappings)
            }
            
            return college_uni_agreement
        except Exception as e:
            print(f"Error generating simplified articulation group: {str(e)}")
            traceback.print_exc()
            raise
    
    @staticmethod
    def create_transfer_plan(db: Session, college_id: int, university_id: int, major_id: int, num_of_terms: int):
        """Create a transfer plan for a student."""
        # Get basic information
        basic_info = TransferPlanService.get_basic_info(db, college_id, university_id, major_id)
        articulation_groups = db_get_articulation_group_filtered(db, college_id, university_id, major_id)

        if not articulation_groups:
            return {"error": "No articulation agreements found for this combination"}
        
        uni_to_cc_map = {}  # Maps university courses to CC courses
        cc_to_uni_map = {}  # Maps CC courses to university courses they satisfy

        # Process articulation groups to build mappings
        ArticulationService.process_map_uni_and_cc(db, articulation_groups, uni_to_cc_map, cc_to_uni_map)
        
        # Get courses to take and their details
        cc_courses_to_take = ArticulationService.get_courses_to_take(uni_to_cc_map)

        # Also get all possible alternative courses
        all_possible_courses = set(cc_courses_to_take)
        for uni_course, cc_alternatives in uni_to_cc_map.items():
            all_possible_courses.update(cc_alternatives)

        # Query for all courses including alternatives
        courses = db.query(Courses).filter(
            Courses.college_id == college_id,
            Courses.code.in_(all_possible_courses)
        ).all()

        course_details = TransferPlanService.extract_course_details(courses)
        
        # Build prerequisite graph and sort courses
        prerequisite_graph, _ = PrerequisiteService.build_prerequisite_graph(db, college_id)
        sorted_courses = PrerequisiteService.topological_sort(prerequisite_graph)
        sorted_courses = [c for c in sorted_courses if c in cc_courses_to_take]

        # Create term plan
        term_plan = CourseSchedulingService.plan_course_sequence(sorted_courses, num_of_terms, prerequisite_graph)

        uni_course_alternatives = TransferPlanService.map_alternatives_cc_classes(uni_to_cc_map)
        print("===============================================")
        print(f"University course alternatives: {uni_course_alternatives}")
        print("===============================================")

        # Format the plan
        formatted_plan = {
            "university": basic_info["university"].university_name,
            "college": basic_info["college"].college_name,
            "major": basic_info["major"].major_name,
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
                # Get university courses this CC course satisfies
                satisfies_uni_courses = cc_to_uni_map.get(cc_course, [])
                
                # Find alternatives for each university course this satisfies
                alternatives = set()
                for uni_course in satisfies_uni_courses:
                    # Get all CC courses that satisfy this uni course
                    alt_cc_courses = uni_course_alternatives.get(uni_course, [])
                    
                    # Remove the current course from alternatives
                    course_alternatives = [alt for alt in alt_cc_courses if alt != cc_course]
                    alternatives.update(course_alternatives)
                
                # Add course to the term plan with details
                course_info = {
                    "code": cc_course,
                    "name": course_details.get(cc_course, {}).get("name", "Unknown Course"),
                    "units": course_details.get(cc_course, {}).get("units", 0),
                    "satisfies_university_courses": satisfies_uni_courses
                }
                
                # Add alternatives if they exist
                if alternatives:
                    # Get course details for alternatives to include names
                    alternative_details = []
                    for alt_code in alternatives:
                        alt_detail = {
                            "code": alt_code,
                            "name": course_details.get(alt_code, {}).get("name", "Unknown Course"),
                            "units": course_details.get(alt_code, {}).get("units", 0)
                        }
                        alternative_details.append(alt_detail)
                    
                    course_info["alternatives"] = alternative_details
                
                term_data["courses"].append(course_info)
                completed_courses.add(cc_course)
            
            formatted_plan["term_plan"].append(term_data)
        
        # Handle multiple entries for the same university course
        StudentProgressService.consolidate_university_courses(formatted_plan)
        
        return formatted_plan   