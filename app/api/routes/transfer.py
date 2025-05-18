from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.services.transfer_service import (
    get_articulation_groups,
    simplified_articulation_group
)


router = APIRouter(
    prefix="/transfer-plan",
    tags=["Transfer Plan"]
)



@router.get("/articulation_group")
def get_articulation_group(
    college_id: int,
    university_id: int,
    major_id: int,
    db: Session = Depends(get_db)
):
    try:
        articulation_group = get_articulation_groups(db, college_id, university_id, major_id)
        return articulation_group
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simplied_plan")
def simplied_plan(
    college_id: int,
    university_id: int,
    major_id: int,
    db: Session = Depends(get_db)
):
    try:
        articulation_group = simplified_articulation_group(db, college_id, university_id, major_id)
        return articulation_group
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    