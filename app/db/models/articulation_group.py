from sqlalchemy import Column, Integer, ForeignKey, ARRAY, Enum
from sqlalchemy.orm import relationship
from app.db.connection import Base
import enum

class RelationshipType(enum.Enum):
    AND = "AND"
    OR = "OR"


class ArticulationGroup(Base):
    __tablename__ = "articulation_group"

    id = Column(Integer, primary_key=True, index=True)
    university_course_ids = Column(ARRAY(Integer), nullable=False)
    operator = Column(Enum(RelationshipType), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)

    # Relationships
    major = relationship("Majors", back_populates="articulation_groups")
    university = relationship("Universities", back_populates="articulation_groups")
    courses = relationship("ArticulationGroupCourses", back_populates="articulation_group")

