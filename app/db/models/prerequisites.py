from sqlalchemy import Column, Integer, ForeignKey, Enum
import enum
from sqlalchemy.orm import relationship
from app.db.connection import Base


class PrerequisiteType(enum.Enum):
    REQUIRED = "required"
    COREQUISITE = "corequisite"
    RECOMMENDED = "recommended"


class Prerequisites(Base):
    __tablename__ = "prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    prerequisite_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    prerequisite_type = Column(Enum(PrerequisiteType), nullable=False, default=PrerequisiteType.REQUIRED)

    # Relationships:
    course = relationship("Courses", foreign_keys=[course_id], back_populates="prerequisites")
    prerequisite = relationship("Courses", foreign_keys=[prerequisite_course_id], back_populates="is_prerequisite_for")