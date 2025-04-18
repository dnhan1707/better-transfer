from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.connection import Base

class CourseMajorMapping(Base):
    __tablename__ = "course_major_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    university_course_id = Column(Integer, ForeignKey("university_courses.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    
    # Relationships
    university_course = relationship("UniversityCourses", back_populates="major_mappings")
    major = relationship("Majors", back_populates="course_mappings")
    
    # Ensure no duplicate mappings
    __table_args__ = (
        UniqueConstraint('university_course_id', 'major_id', name='unq_course_major'),
    )