from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import TransferPlanRequest


transfer_plan_service = TransferPlanService()
router = APIRouter(
    prefix="/transfer-plan",
    tags=["Transfer Plan"]
)


@router.post("/")
def transfer_plan(
    request: TransferPlanRequest,
    db: Session = Depends(get_db)
):
    try:
        plan = transfer_plan_service.create_transfer_plan(db, request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
