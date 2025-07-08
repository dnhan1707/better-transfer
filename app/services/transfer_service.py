from sqlalchemy.orm import Session
from app.db.queries.institution_queries import db_get_basic_info
from app.schemas.transferPlanRequest import FullRequest, ReOrderRequestModel
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.utils.logging_config import get_logger
import json
import traceback

logger = get_logger(__name__)

class TransferPlanService:
    """Service for generating transfer plans."""
    def __init__(self):
        self.vector_store = VectorStore()
        self.synthesizer = Synthesizer()


    async def create_RAG_transfer_plan_v2(self, app_db: Session, vector_db: Session, full_request: FullRequest):
        try:
            # Validate input
            if not full_request.request:
                return {"error": "No transfer plan requests provided"}
        
            # Get information for all requested university-major combinations
            target_combinations = []
            college = None
            
            for request in full_request.request:
                basic_info = db_get_basic_info(app_db, request)
                if not basic_info:
                    logger.error(f"Could not find information for request: {request}")
                    continue
                    
                # All requests have the same college
                if not college:
                    college = basic_info["college"]
                    
                target_combinations.append({
                    "college": basic_info["college"],
                    "university": basic_info["university"],
                    "major": basic_info["major"]
                })
            
            if not target_combinations:
                return {"error": "No valid university-major combinations found"}
                
            # Build the multi-target query
            query_parts = ["Create an optimized transfer plan from " + college + " that satisfies requirements for:"]
            for idx, target in enumerate(target_combinations):
                query_parts.append(f"{idx+1}. {target['university']} - {target['major']}")
            query_parts.append(f"Duration: {full_request.number_of_terms} terms.")
            query_parts.append("Find courses that satisfy requirements for multiple universities when possible.")
            query = "\n".join(query_parts)
            
            # Get context for all targets at once
            vector_res = await self.vector_store.vector_search_v2(vector_db, query, target_combinations)
            
            # Generate the optimized plan
            result = await self.synthesizer.generate_response(question=query, number_of_terms=full_request.number_of_terms, vector_res=vector_res)
            
            return result
                
        except Exception as e:
            logger.error(f"Error RAG creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
        

    async def re_order_transfer_plan_v1(self, app_db: Session, vector_db: Session, request: ReOrderRequestModel):
        try:
            if not request.taken_classes or len(request.taken_classes) == 0:
                logger.error("No taken classes provided in request")
                return {"error": "Please specify at least one taken course"}
            
            original_plan = request.original_plan.model_dump()
            taken_classes = request.taken_classes
            source_college = request.original_plan.source_college
            courses_data = await self.vector_store.get_courses_data(vector_db, source_college)

            user_prompt = f"""
                # Original Transfer Plan Structure (to maintain)
                {json.dumps(original_plan, indent=2)}

                # Courses Already Taken (remove these)
                {json.dumps(taken_classes, indent=2)}

                # Instructions
                Please reorganize the transfer plan while:
                1. Preserving the EXACT same JSON structure shown above
                2. Removing all courses in the "taken_classes" list
                3. Redistributing remaining courses across the same number of terms
                4. Maintaining prerequisite ordering
            """

            return await self.synthesizer.generate_reorder_plan_response(user_prompt, courses_data)
            

        except Exception as e:
            logger.error(f"Error RAG re-order transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}