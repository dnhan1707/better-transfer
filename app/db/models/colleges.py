from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.connection import Base


class Colleges(Base):
    __tablename__="colleges"

    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String, unique=True, index=True, nullable=False)
    courses = relationship("Courses", back_populates="college", cascade="all, delete")  
    articulation_groups = relationship("ArticulationGroup", back_populates="college")