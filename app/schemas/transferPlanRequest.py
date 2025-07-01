from pydantic import BaseModel, Field, field_validator


class TransferPlanRequest(BaseModel):
    """Base model for institution identifiers used across services"""
    college_id: int = Field(..., description="Community College Id")
    university_id: int = Field(..., description="University Id")
    major_id: int = Field(..., description="Major Id")
    number_of_terms: int = Field(default=4, description="Number of Semesters")

    @field_validator('college_id', 'university_id', 'major_id')
    def validate_ids_positive(cls, v):
        if v <= 0:
            raise ValueError("IDs must be positive integers")
        return v    
