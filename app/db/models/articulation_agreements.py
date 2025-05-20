from sqlalchemy import Column, Integer, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from app.db.connection import Base
import enum

class ArticulationRelationshipType(enum.Enum):
    AND = "AND"  
    OR = "OR"    

class ArticulationAgreements(Base):
    __tablename__ = "articulation_agreements"

    id = Column(Integer, primary_key=True, index=True)
    community_college_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    university_course_id = Column(Integer, ForeignKey("university_courses.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    
    # Relation to expression structure
    group_id = Column(String, nullable=False, default="default")  # To group related articulations
    relationship_type = Column(Enum(ArticulationRelationshipType), nullable=False, default=ArticulationRelationshipType.OR)

    # Relationships
    community_college_course = relationship("Courses", back_populates="articulations")
    university_course = relationship("UniversityCourses", back_populates="articulations")
    university = relationship("Universities", back_populates="articulations")
    major = relationship("Majors", back_populates="articulations")