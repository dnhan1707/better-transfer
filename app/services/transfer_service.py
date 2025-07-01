from sqlalchemy.orm import Session
from app.db.queries.institution_queries import db_get_basic_info
from app.schemas.transferPlanRequest import TransferPlanRequest
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


    async def create_RAG_transfer_plan_v2(self, app_db: Session, vector_db: Session, request: TransferPlanRequest):
        try:            
            basic_info = db_get_basic_info(app_db, request)
            
            if not basic_info:
                logger.error("Basic information not found")
                return {"error": "Institution information not found"}
            
            # Access .name properties of the model objects
            query = f"""
            Transfer plan for {basic_info["major"].major_name} major.
            Target university: {basic_info["university"].university_name}.
            Starting college: {basic_info["college"].college_name}.
            Duration: {request.number_of_terms} terms.
            Required: All courses and prerequisites needed to transfer successfully, including any acceptable alternative courses that may satisfy the same requirements.
            """

            vector_res = await self.vector_store.vector_search_v2(vector_db, query, basic_info)
            return await self.synthesizer.generate_response(question=query, vector_res=vector_res)
            
        
        except Exception as e:
            logger.error(f"Error RAG creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
