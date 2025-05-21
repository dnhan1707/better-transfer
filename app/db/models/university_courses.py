from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class UniversityCourses(Base):
    __tablename__ = "university_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    course_code = Column(String, nullable=False)
    # major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)

    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    university = relationship("Universities", back_populates="university_courses")
    
    # New relationship to CourseMajorMapping
    major_mappings = relationship("CourseMajorMapping", back_populates="university_course")
    articulations = relationship("ArticulationAgreements", back_populates="university_course")
    expression_nodes = relationship("ExpressionNode", 
                                   back_populates="university_course", 
                                   viewonly=True)