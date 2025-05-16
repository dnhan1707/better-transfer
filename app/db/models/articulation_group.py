from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.connection import Base

class ArticulationGroup(Base):
    __tablename__ = "articulation_group"

    id = Column(Integer, primary_key=True, index=True)

    # Institution and scope info
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)

    # JSON-based logical expression
    expression = Column(JSON, nullable=False)  # example: {"operator": "AND", "groups": [...]}

    # Relationships
    major = relationship("Majors", back_populates="articulation_groups")
    university = relationship("Universities", back_populates="articulation_groups")
    college = relationship("Colleges", back_populates="articulation_groups")
    courses = relationship("ArticulationGroupCourses", back_populates="articulation_group")