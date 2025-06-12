from sqlalchemy.orm import Session
from app.services.articulation_service import ArticulationService
from app.services.course_service import CourseSchedulingService
from app.db.models.courses import Courses


class CourseDetailService:
    def __init__(self):
        self.course_scheduling_service = CourseSchedulingService()
        self.articulation_service = ArticulationService()

    def get_course_details(self, db: Session, college_id: int, uni_to_cc_map):
        """Get courses to take and their details."""
        cc_courses_to_take = self.articulation_service.get_courses_to_take(uni_to_cc_map)
        
        # Get all possible courses including alternatives
        all_possible_courses = set(cc_courses_to_take)
        for _, cc_alternatives in uni_to_cc_map.items():
            all_possible_courses.update(cc_alternatives)
        
        courses = db.query(Courses).filter(
            Courses.college_id == college_id,
            Courses.code.in_(all_possible_courses)
        ).all()
        
        course_details = self.course_scheduling_service.extract_course_details(courses)
        return cc_courses_to_take, course_details