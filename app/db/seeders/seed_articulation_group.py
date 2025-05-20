import os
import json
from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.articulation_group import ArticulationGroup
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.university_courses import UniversityCourses
from app.db.models.expression_node import ExpressionNode, NodeType, OperatorType


def create_nodes_from_expression(db, group_id, expression, parent_id=None):
    """Recursively create nodes from a JSON expression"""
    if not expression:
        return None
        
    # Create operator node
    if isinstance(expression, dict) and "operator" in expression:
        operator = expression["operator"]
        node = ExpressionNode(
            group_id=group_id,
            parent_node_id=parent_id,
            node_type=NodeType.OPERATOR,
            operator_type=OperatorType.AND if operator == "AND" else OperatorType.OR
        )
        db.add(node)
        db.flush()  # To get the node ID
        
        # Process children
        for child in expression.get("groups", []):
            create_nodes_from_expression(db, group_id, child, node.id)
            
        return node.id
    
    # Create course node
    elif isinstance(expression, str):
        # Find the university course ID
        uni_course = db.query(UniversityCourses).filter(
            UniversityCourses.course_code == expression
        ).first()
        
        if uni_course:
            node = ExpressionNode(
                group_id=group_id,
                parent_node_id=parent_id,
                node_type=NodeType.COURSE,
                university_course_id=uni_course.id
            )
            db.add(node)
            db.flush()
            return node.id
    
    return None

def seed_articulation_groups(db: Session):
    """Seed articulation groups and their expression nodes"""
    from app.db.models.expression_node import ExpressionNode, NodeType, OperatorType
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "seed_data", "articulation_group.json")
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} articulation groups to seed")
    groups_created = 0
    
    for item in data:
        # Look up related entities
        university = db.query(Universities).filter(
            Universities.university_name == item["university_name"]
        ).first()
        major = db.query(Majors).filter(
            Majors.major_name == item["major_name"]
        ).first()
        college = db.query(Colleges).filter(
            Colleges.college_name == item["college_name"]
        ).first()
        
        if not university or not major or not college:
            print(f"Missing related entity for {item}")
            continue
            
        # Create the group
        group = ArticulationGroup(
            university_id=university.id,
            major_id=major.id,
            college_id=college.id,
            name=item.get("name", f"{major.major_name} requirements")
        )
        db.add(group)
        db.flush()  # Get the ID
        
        # Process the expression into nodes
        root_node_id = create_nodes_from_expression(db, group.id, item["expression"])
        
        # Set the root node reference
        if root_node_id:
            group.root_expression_node_id = root_node_id
            
        groups_created += 1
    
    # Add this line to commit all changes to the database
    db.commit()
    
    print(f"Successfully created {groups_created} articulation groups")