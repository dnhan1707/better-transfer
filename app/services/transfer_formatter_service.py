from app.services.student_progress_service import StudentProgressService
from app.services.course_service import CourseSchedulingService

class TransferPlanFormatter:
    def __init__(self):
        self.course_service = CourseSchedulingService()
        self.student_progress_service = StudentProgressService()

    def format_alternatives(self, alternatives, course_details):
        """Format details for alternative courses."""
        return [{
            "code": alt_code,
            "name": course_details.get(alt_code, {}).get("name", "Unknown Course"),
            "units": course_details.get(alt_code, {}).get("units", 0)
        } for alt_code in alternatives]
    

    def format_term_data(self, term_index, term_courses, cc_to_uni_map, uni_course_alternatives, course_details, completed_courses):
        """Format data for a single term."""
        term_data = {
            "term": term_index + 1,
            "courses": []
        }
        
        for cc_course in term_courses:
            satisfies_uni_courses = cc_to_uni_map.get(cc_course, [])
            alternatives = self.course_service.get_course_alternatives(cc_course, satisfies_uni_courses, uni_course_alternatives)
            
            course_info = {
                "code": cc_course,
                "name": course_details.get(cc_course, {}).get("name", "Unknown Course"),
                "units": course_details.get(cc_course, {}).get("units", 0),
                "satisfies_university_courses": satisfies_uni_courses
            }
            
            if alternatives:
                course_info["alternatives"] = self.format_alternatives(alternatives, course_details)
            
            term_data["courses"].append(course_info)
            completed_courses.add(cc_course)
        
        return term_data
    

    def format_transfer_plan(self, basic_info, term_plan, cc_to_uni_map, uni_course_alternatives, course_details):
        """Format the transfer plan with course details."""
        formatted_plan = {
            "university": basic_info["university"].university_name,
            "college": basic_info["college"].college_name,
            "major": basic_info["major"].major_name,
            "term_plan": []
        }
        
        completed_courses = set()
        for term_index, term_courses in enumerate(term_plan):
            term_data = self.format_term_data(
                term_index, term_courses, cc_to_uni_map, 
                uni_course_alternatives, course_details, completed_courses
            )
            formatted_plan["term_plan"].append(term_data)
        
        self.student_progress_service.consolidate_university_courses(formatted_plan)
        return formatted_plan
    
