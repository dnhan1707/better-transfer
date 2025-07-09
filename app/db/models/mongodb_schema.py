from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Any, Optional


class CoursePrerequisite(BaseModel):
    college: str
    course_code: str
    name: str
    units: float
    difficulty: int
    assessment_allow: bool
    prerequisite: List[List[str]]
    unlocks: List[str]
    department: str

    class Config: 
        schema_extra = {
            "example": {
                "college": "Pasadena City College",
                "course_code": "CS 002",
                "name": "Fundamentals of Computer Science I",
                "units": 4.0,
                "difficulty": 4,
                "assessment_allow": False,
                "prerequisites": [["MATH 008"], ["MATH 009"]],
                "unlocks": ["CS 003A", "CS 006"],
                "department": "computer science"
            }
        }
