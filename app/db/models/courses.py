from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class Courses(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    units = Column(Float, nullable=False)
    difficulty = Column(Integer, nullable=False)

    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    college = relationship("Colleges", back_populates="courses", cascade="all, delete")
    articulations = relationship("ArticulationAgreements", back_populates="community_college_course", cascade="all, delete")
    prerequisites = relationship("Prerequisites", foreign_keys="[Prerequisites.course_id]", back_populates="course")
    is_prerequisite_for = relationship("Prerequisites", foreign_keys="[Prerequisites.prerequisite_course_id]", back_populates="prerequisite")
    articulation_groups = relationship("ArticulationGroupCourses", back_populates="community_college_course")