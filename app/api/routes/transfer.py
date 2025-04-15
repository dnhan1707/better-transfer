from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.services.transfer_service import generate_transfer_plan
from app.schemas.transfer import TransferPlanCourse


router = APIRouter(
    prefix="/transfer-plan",
    tags=["Transfer Plan"]
)


@router.get("/", response_model=List[TransferPlanCourse])
def get_transfer_plan(
    college_id: int,
    university_id: int,
    major_id: int,
    db: Session = Depends(get_db)
):
    try:
        plan = generate_transfer_plan(db, college_id, university_id, major_id)
        return plan
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))