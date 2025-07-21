from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class InstitutionIds(BaseModel):
    collegeId: str = Field(..., description="College Id")
    universityId: str = Field(..., description="University Id")
    majorId: str = Field(..., description="Major Id")


class InputRequest(BaseModel):
    targets: List[InstitutionIds] = Field(..., description="List of college, university and major Id")
    number_of_terms: int = Field(..., description="Number of terms in total")

class TransferPlanRequest(BaseModel):
    """Base model for institution identifiers used across services"""
    college_id: int = Field(..., description="Community College Id")
    university_id: int = Field(..., description="University Id")
    major_id: int = Field(..., description="Major Id")

    @field_validator('college_id', 'university_id', 'major_id')
    def validate_ids_positive(cls, v):
        if v <= 0:
            raise ValueError("IDs must be positive integers")
        return v    


class FullRequest(BaseModel):
    request: List[TransferPlanRequest] = Field(..., description="List of TransferPlanRequest")
    number_of_terms: int = Field(default=4, description="Number of Semesters")


class TargetInstitution(BaseModel):
    university: str = Field(..., description="University Name")
    major: str = Field(..., description="Major")
    id: Optional[int] = None  # Made optional

class SatisfiedUniCourse(BaseModel):
    university: str
    major: str
    university_courses: List[str] = Field(..., description="List of university course code")


class CourseModel(BaseModel):
    code: str = Field(..., description="Course code")
    name: str = Field(..., description="Course name/description")
    units: float = Field(..., description="Course units")  # Changed from unit to units
    difficulty: int = Field(..., description="Course difficulty 1 to 5")
    prerequisites: List[str] = Field(default=[], description="List of prerequisite course code")
    satisfies: List[SatisfiedUniCourse] = Field(default=[], description="List of satisfied course code")
    alternatives: List[str] = Field(default=[])  # Made optional with default
    note: Optional[str] = None  # Made optional


class TermPlanModel(BaseModel):
    term: int = Field(..., description="Term number")
    courses: List[CourseModel] = Field(..., description="Course detail")


class UnscheduledCourseModel(BaseModel):
    code: str
    reason: str


class FullTransferPlanModel(BaseModel):
    targets: List[TargetInstitution]
    source_college: str
    term_plan: List[TermPlanModel]
    unscheduled_courses: Optional[List[UnscheduledCourseModel]]


class ReOrderRequestModel(BaseModel):
    original_plan: FullTransferPlanModel
    taken_classes: List[str] = Field(..., description="List of taken classes code")