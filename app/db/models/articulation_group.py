from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.connection import Base

class ArticulationGroup(Base):
    __tablename__ = "articulation_group"

    id = Column(Integer, primary_key=True, index=True)

    # Institution and scope info
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    
    # Name/description of this requirement group
    name = Column(String, nullable=True)
    
    # Reference to the root node of the expression tree
    root_expression_node_id = Column(Integer, ForeignKey("expression_nodes.id"), nullable=True)
    
    # Removed the JSON expression field
    # expression = Column(JSON, nullable=False)  # example: {"operator": "AND", "groups": [...]}

    # Relationships
    major = relationship("Majors", back_populates="articulation_groups")
    university = relationship("Universities", back_populates="articulation_groups")
    college = relationship("Colleges", back_populates="articulation_groups")
    expression_nodes = relationship(
        "ExpressionNode", 
        back_populates="articulation_group",
        foreign_keys="ExpressionNode.group_id"  
    )    
    root_node = relationship(
        "ExpressionNode", 
        foreign_keys=[root_expression_node_id],
        uselist=False
    )