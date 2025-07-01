from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.connection import get_db, get_vector_db
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import TransferPlanRequest


def create_transfer_router() -> APIRouter:
    transfer_plan_service = TransferPlanService()
    router = APIRouter(
        prefix="/transfer-plan",
        tags=["Transfer Plan"]
    )
        
    @router.post("/v2/rag")
    async def rag_transfer_plan_v2(
        request:     TransferPlanRequest,
        app_db:      Session = Depends(get_db),
        vector_db:   Session = Depends(get_vector_db), 
    ):
        try:
            return await transfer_plan_service.create_RAG_transfer_plan_v2(app_db, vector_db, request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    return router
