from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class UniversityCourses(Base):
    __tablename__ = "university_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    course_code = Column(String, nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)

    # Relationships
    major = relationship("Majors", back_populates="university_courses")
    articulations = relationship("ArticulationAgreements", back_populates="university_course", cascade="all, delete")