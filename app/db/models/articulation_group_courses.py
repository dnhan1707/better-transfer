from sqlalchemy import Column, Integer, ForeignKey, ARRAY, Enum
from sqlalchemy.orm import relationship
from app.db.connection import Base


class ArticulationGroupCourses(Base):
    __tablename__ = "articulation_group_courses"

    id = Column(Integer, primary_key=True, index=True)
    articulation_group_id = Column(Integer, ForeignKey("articulation_group.id"), nullable=False)
    community_college_course_id = Column(Integer, ForeignKey("courses.id") ,nullable=False)

    # Relationships
    articulation_group = relationship("ArticulationGroup", back_populates="courses")    
    community_college_course = relationship("Courses", back_populates="articulation_groups")
