from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.services.transfer_service import TransferPlanService

transfer_plan_service = TransferPlanService()
router = APIRouter(
    prefix="/transfer-plan",
    tags=["Transfer Plan"]
)


@router.get("/")
def transfer_plan(
    college_id: int,
    university_id: int,
    major_id: int,
    db: Session = Depends(get_db)
):
    try:
        plan = transfer_plan_service.create_transfer_plan(db, college_id, university_id, major_id, num_of_terms=5)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
