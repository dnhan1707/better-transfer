from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import TransferPlanRequest


def create_transfer_router() -> APIRouter:
    transfer_plan_service = TransferPlanService()
    router = APIRouter(
        prefix="/transfer-plan",
        tags=["Transfer Plan"]
    )


    @router.post("/")
    async def transfer_plan(
        request: TransferPlanRequest,
        db: Session = Depends(get_db)
    ):
        try:
            plan = await transfer_plan_service.create_transfer_plan(db, request)
            return plan
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    
    @router.post("/rag")
    async def RAG_transfer_plan(
        request: TransferPlanRequest,
        db: Session = Depends(get_db)
    ):
        try:
            plan = await transfer_plan_service.create_RAG_transfer_plan(db, request)
            return plan
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    return router
