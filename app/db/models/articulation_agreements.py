from sqlalchemy import Column, Integer, ForeignKey, Enum, String, JSON
from sqlalchemy.orm import relationship
from app.db.connection import Base
import enum

class RelationshipType(enum.Enum):
    AND = "AND"
    OR = "OR"

class ArticulationAgreements(Base):
    __tablename__ = "articulation_agreements"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Store logical expression as a JSON structure
    # Example: {"operator": "AND", "groups": [
    #   {"operator": "OR", "groups": [1, 2]}, 
    #   {"id": 3}
    # ]}
    expression = Column(JSON, nullable=False)

    # Relationships
    university = relationship("Universities", back_populates="articulation_agreements")
    major = relationship("Majors", back_populates="articulation_agreements")