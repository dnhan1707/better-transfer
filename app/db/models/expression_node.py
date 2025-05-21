from sqlalchemy import Column, Integer, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from app.db.connection import Base
import enum

class NodeType(enum.Enum):
    OPERATOR = "OPERATOR"
    COURSE = "COURSE"

class OperatorType(enum.Enum):
    AND = "AND"
    OR = "OR"

class ExpressionNode(Base):
    __tablename__ = "expression_nodes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Tree structure
    group_id = Column(Integer, ForeignKey("articulation_group.id"), nullable=False)
    parent_node_id = Column(Integer, ForeignKey("expression_nodes.id"), nullable=True)
    
    # Node type and content
    node_type = Column(Enum(NodeType), nullable=False)
    operator_type = Column(Enum(OperatorType), nullable=True)  # Only used when node_type is OPERATOR
    university_course_id = Column(Integer, ForeignKey("university_courses.id"), nullable=True)  # Only used when node_type is COURSE
    
    # Relationships
    articulation_group = relationship(
        "ArticulationGroup", 
        back_populates="expression_nodes",
        foreign_keys=[group_id]  # Specify the foreign key
    )    
    parent_node = relationship("ExpressionNode", back_populates="child_nodes", remote_side=[id])
    child_nodes = relationship("ExpressionNode", back_populates="parent_node")
    university_course = relationship(
        "UniversityCourses", 
        back_populates="expression_nodes",
        foreign_keys=[university_course_id],
        viewonly=True  # This avoids the circular dependency issue
    )