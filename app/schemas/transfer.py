from pydantic import BaseModel

class TransferPlanCourse(BaseModel):
    course_id: int
    code: str
    name: str
    units: float
    difficulty: int

    model_config = {
        "from_attributes": True  
    }