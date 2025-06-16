from sqlalchemy.orm import Session
from app.db.queries.institution_queries import db_get_basic_info
from app.db.queries.articulation_queries import db_get_articulation_group_filtered
from app.services.course_service import CourseSchedulingService
from app.services.articulation_service import ArticulationService
from app.schemas.transferPlanRequest import TransferPlanRequest
from app.services.transfer_formatter_service import TransferPlanFormatter
from app.services.course_detail_service import CourseDetailService

import traceback

class TransferPlanService:
    """Service for generating transfer plans."""
    def __init__(self):
        self.formatter = TransferPlanFormatter()
        self.course_service = CourseSchedulingService()
        self.articulation_service = ArticulationService()
        self.course_detail_service = CourseDetailService()

    async def create_transfer_plan(self, db: Session, request: TransferPlanRequest):
        """Create a transfer plan for a student."""
        try:
            # Get basic information and articulation agreements
            basic_info = db_get_basic_info(db, request)        
            articulation_groups = db_get_articulation_group_filtered(db, request)
            
            # Build course mappings
            uni_to_cc_map, cc_to_uni_map = self.articulation_service.process_map_uni_and_cc(db, articulation_groups)
            
            # Get course details
            cc_courses_to_take, course_details = self.course_detail_service.get_course_details(db, request.college_id, uni_to_cc_map)
            
            # Sort courses by prerequisites
            prerequisite_graph, sorted_courses = self.course_service.prepare_course_sequence(db, request.college_id, cc_courses_to_take)
            
            # Create and format term plan
            term_plan = self.course_service.plan_course_sequence(sorted_courses, request.number_of_terms, prerequisite_graph)               
            uni_course_alternatives = self.articulation_service.map_alternatives_cc_classes(uni_to_cc_map)
            
            # Format the final plan
            formatted_plan = self.formatter.format_transfer_plan(
                basic_info, term_plan, cc_to_uni_map, uni_course_alternatives, course_details
            )
            
            return formatted_plan
        except Exception as e:
            print(f"Error creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}


    