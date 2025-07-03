from sqlalchemy.orm import Session
from app.db.queries.institution_queries import db_get_basic_info
from app.schemas.transferPlanRequest import FullRequest
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.utils.logging_config import get_logger

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
            result = await self.synthesizer.generate_response(question=query, vector_res=vector_res)
            
            return result
                
        except Exception as e:
            logger.error(f"Error RAG creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}