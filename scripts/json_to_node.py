from app.db.connection import SessionLocal
from app.db.models.articulation_group import ArticulationGroup
from app.db.models.expression_node import ExpressionNode, NodeType, OperatorType
from app.db.models.university_courses import UniversityCourses

def convert_json_to_nodes():
    """Convert JSON expressions to normalized nodes"""
    db = SessionLocal()
    
    try:
        # Get all articulation groups
        groups = db.query(ArticulationGroup).all()
        
        for group in groups:
            # Skip if no expression
            if not hasattr(group, 'expression') or not group.expression:
                continue
                
            # Convert JSON expression to nodes
            create_nodes_from_expression(db, group.id, group.expression)
            
        db.commit()
        print(f"Successfully converted {len(groups)} articulation groups to normalized structure")
    except Exception as e:
        db.rollback()
        print(f"Error converting expressions: {str(e)}")
    finally:
        db.close()

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

if __name__ == "__main__":
    convert_json_to_nodes()