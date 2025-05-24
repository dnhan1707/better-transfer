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
    def map_alternatives_cc_classes(uni_to_cc_map):
        uni_course_alternatives = {}
        for uni_course, cc_courses in uni_to_cc_map.items():
            uni_course_alternatives[uni_course] = cc_courses
        
        return uni_course_alternatives

    @staticmethod
    def create_transfer_plan(db: Session, college_id: int, university_id: int, major_id: int, num_of_terms: int):
        """Create a transfer plan for a student."""
        try:
            # Get basic information and articulation agreements
            basic_info, articulation_groups = TransferPlanService._get_plan_basic_info(db, college_id, university_id, major_id)
            
            # Build course mappings
            uni_to_cc_map, cc_to_uni_map = TransferPlanService._build_course_mappings(db, articulation_groups)
            
            # Get course details
            cc_courses_to_take, course_details = TransferPlanService._get_course_details(db, college_id, uni_to_cc_map)
            
            # Sort courses by prerequisites
            prerequisite_graph, sorted_courses = TransferPlanService._prepare_course_sequence(db, college_id, cc_courses_to_take)
            
            # Create and format term plan
            term_plan = CourseSchedulingService.plan_course_sequence(sorted_courses, num_of_terms, prerequisite_graph)
            uni_course_alternatives = TransferPlanService.map_alternatives_cc_classes(uni_to_cc_map)
            
            # Format the final plan
            formatted_plan = TransferPlanService._format_transfer_plan(
                basic_info, term_plan, cc_to_uni_map, uni_course_alternatives, course_details
            )
            
            return formatted_plan
        except Exception as e:
            print(f"Error creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}

    @staticmethod
    def _get_plan_basic_info(db: Session, college_id: int, university_id: int, major_id: int):
        """Get basic information and check articulation agreements."""
        basic_info = TransferPlanService.get_basic_info(db, college_id, university_id, major_id)
        articulation_groups = db_get_articulation_group_filtered(db, college_id, university_id, major_id)
        
        if not articulation_groups:
            raise ValueError("No articulation agreements found for this combination")
        
        return basic_info, articulation_groups

    @staticmethod
    def _build_course_mappings(db: Session, articulation_groups):
        """Build mappings between university and CC courses."""
        uni_to_cc_map = {}  # Maps university courses to CC courses
        cc_to_uni_map = {}  # Maps CC courses to university courses they satisfy
        
        ArticulationService.process_map_uni_and_cc(db, articulation_groups, uni_to_cc_map, cc_to_uni_map)
        return uni_to_cc_map, cc_to_uni_map

    @staticmethod
    def _get_course_details(db: Session, college_id: int, uni_to_cc_map):
        """Get courses to take and their details."""
        cc_courses_to_take = ArticulationService.get_courses_to_take(uni_to_cc_map)
        
        # Get all possible courses including alternatives
        all_possible_courses = set(cc_courses_to_take)
        for _, cc_alternatives in uni_to_cc_map.items():
            all_possible_courses.update(cc_alternatives)
        
        courses = db.query(Courses).filter(
            Courses.college_id == college_id,
            Courses.code.in_(all_possible_courses)
        ).all()
        
        course_details = TransferPlanService.extract_course_details(courses)
        return cc_courses_to_take, course_details

    @staticmethod
    def _prepare_course_sequence(db: Session, college_id: int, cc_courses_to_take):
        """Build prerequisite graph and sort courses."""
        prerequisite_graph, _ = PrerequisiteService.build_prerequisite_graph(db, college_id)
        sorted_courses = PrerequisiteService.topological_sort(prerequisite_graph)
        sorted_courses = [c for c in sorted_courses if c in cc_courses_to_take]
        return prerequisite_graph, sorted_courses

    @staticmethod
    def _format_transfer_plan(basic_info, term_plan, cc_to_uni_map, uni_course_alternatives, course_details):
        """Format the transfer plan with course details."""
        formatted_plan = {
            "university": basic_info["university"].university_name,
            "college": basic_info["college"].college_name,
            "major": basic_info["major"].major_name,
            "term_plan": []
        }
        
        completed_courses = set()
        for term_index, term_courses in enumerate(term_plan):
            term_data = TransferPlanService._format_term_data(
                term_index, term_courses, cc_to_uni_map, 
                uni_course_alternatives, course_details, completed_courses
            )
            formatted_plan["term_plan"].append(term_data)
        
        StudentProgressService.consolidate_university_courses(formatted_plan)
        return formatted_plan

    @staticmethod
    def _format_term_data(term_index, term_courses, cc_to_uni_map, uni_course_alternatives, course_details, completed_courses):
        """Format data for a single term."""
        term_data = {
            "term": term_index + 1,
            "courses": []
        }
        
        for cc_course in term_courses:
            satisfies_uni_courses = cc_to_uni_map.get(cc_course, [])
            alternatives = TransferPlanService._get_course_alternatives(cc_course, satisfies_uni_courses, uni_course_alternatives)
            
            course_info = {
                "code": cc_course,
                "name": course_details.get(cc_course, {}).get("name", "Unknown Course"),
                "units": course_details.get(cc_course, {}).get("units", 0),
                "satisfies_university_courses": satisfies_uni_courses
            }
            
            if alternatives:
                course_info["alternatives"] = TransferPlanService._format_alternatives(alternatives, course_details)
            
            term_data["courses"].append(course_info)
            completed_courses.add(cc_course)
        
        return term_data

    @staticmethod
    def _get_course_alternatives(cc_course, satisfies_uni_courses, uni_course_alternatives):
        """Find alternative courses for a given CC course."""
        alternatives = set()
        for uni_course in satisfies_uni_courses:
            alt_cc_courses = uni_course_alternatives.get(uni_course, [])
            course_alternatives = [alt for alt in alt_cc_courses if alt != cc_course]
            alternatives.update(course_alternatives)
        return alternatives

    @staticmethod
    def _format_alternatives(alternatives, course_details):
        """Format details for alternative courses."""
        return [{
            "code": alt_code,
            "name": course_details.get(alt_code, {}).get("name", "Unknown Course"),
            "units": course_details.get(alt_code, {}).get("units", 0)
        } for alt_code in alternatives]