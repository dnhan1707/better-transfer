from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base


class Majors(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    major_name = Column(String, index=True, nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    
    university = relationship("Universities", back_populates="majors", cascade="all, delete")
    articulations = relationship("ArticulationAgreements", back_populates="major", cascade="all, delete")
    course_mappings = relationship("CourseMajorMapping", back_populates="major")