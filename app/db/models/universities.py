from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from app.db.connection import Base


class Universities(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    university_name = Column(String, unique=True, index=True, nullable=False)
    is_uc = Column(Boolean, nullable=False)
    majors = relationship("Majors", back_populates="university", cascade="all, delete")
    articulations = relationship("ArticulationAgreements", back_populates="university", cascade="all, delete")
    university_courses = relationship("UniversityCourses", back_populates="university")