from sqlalchemy.orm import Session
from app.db.queries.articulation_queries import (
    db_get_cc_courses_with_relationships,
    db_get_cc_courses_for_uni_course,
)
from app.db.models.expression_node import NodeType

class ArticulationService:
    """Service for handling articulation agreements between colleges and universities."""
    def __init__(self):
        pass
    
    def build_course_mappings(self, db: Session, university_id: int, college_id: int):
        """Build mappings between university courses and community college courses."""
        cc_course_mappings = db_get_cc_courses_with_relationships(db, university_id, college_id)
        
        course_mappings = {}
        for mapping in cc_course_mappings:
            uni_course = mapping["university_course"]
            
            # Store both relationship type and courses
            course_mappings[uni_course] = {
                "relationship_type": mapping["relationship_type"],
                "courses": [course["code"] for course in mapping["community_college_courses"]]
            }
        
        return course_mappings
    
    def process_expression(self, expression, course_mappings):
        """Recursively process an expression to build a requirement tree."""
        if not expression:
            return None
            
        operator = expression.get("operator", "AND")
        groups = expression.get("groups", [])
        
        processed_groups = []
        for group in groups:
            if isinstance(group, dict) and "operator" in group:
                # This is a nested expression
                processed_groups.append(self.process_expression(group, course_mappings))
            else:
                # This is a university course code
                uni_course_code = group
                
                # Get relationship type and courses
                mapping = course_mappings.get(uni_course_code, {"relationship_type": "OR", "courses": []})
                relationship_type = mapping["relationship_type"]
                cc_courses = mapping["courses"]
                
                processed_groups.append({
                    "university_course": uni_course_code,
                    "cc_course_relationship": relationship_type,
                    "community_college_courses": cc_courses
                })
        
        return {
            "operator": operator,
            "groups": processed_groups
        }
    
    def build_requirement_tree(self, articulation_groups, course_mappings):
        """Build the requirement tree from articulation groups."""
        if not articulation_groups or len(articulation_groups) == 0:
            return None
            
        if len(articulation_groups) == 1:
            # Just one group, use it directly
            main_group = articulation_groups[0]
            return self.process_expression(main_group.expression, course_mappings)
        else:
            # Multiple groups - combine them into a single AND expression
            combined_expression = {
                "operator": "AND",
                "groups": [group.expression for group in articulation_groups]
            }
            return self.process_expression(combined_expression, course_mappings)
    
    def process_expression_tree(self, db, node, uni_to_cc_map, cc_to_uni_map):
        """Process an expression tree node to map university courses to CC courses and vice versa."""
        if node.node_type == NodeType.COURSE:
            if node.university_course:
                self.map_course_articulations(db, node, uni_to_cc_map, cc_to_uni_map)
        elif node.node_type == NodeType.OPERATOR:
            for child in node.child_nodes:
                self.process_expression_tree(db, child, uni_to_cc_map, cc_to_uni_map)
    
    def map_course_articulations(self, db, node, uni_to_cc_map, cc_to_uni_map):
        """Map a university course to its community college course equivalents."""
        uni_course_code = node.university_course.course_code
        cc_courses = db_get_cc_courses_for_uni_course(
            db, 
            node.university_course.id, 
            node.articulation_group.college_id
        )

        # Map university course -> CC courses
        if uni_course_code not in uni_to_cc_map:
            uni_to_cc_map[uni_course_code] = []
        for course in cc_courses:
            if course.code not in uni_to_cc_map[uni_course_code]:
                uni_to_cc_map[uni_course_code].append(course.code)

        # Map CC courses -> university course
        for cc_course in cc_courses:
            if cc_course.code not in cc_to_uni_map:
                cc_to_uni_map[cc_course.code] = []
            if uni_course_code not in cc_to_uni_map[cc_course.code]:
                cc_to_uni_map[cc_course.code].append(uni_course_code)
    
    def process_map_uni_and_cc(self, db, articulation_groups):
        """Process all articulation groups to build mapping dictionaries."""
        uni_to_cc_map = {}  # Maps university courses to CC courses
        cc_to_uni_map = {}  # Maps CC courses to university courses they satisfy

        for group in articulation_groups:
            # Start from the root node of each articulation group
            if group.root_node:
                self.process_expression_tree(db, group.root_node, uni_to_cc_map, cc_to_uni_map)
        
        return uni_to_cc_map, cc_to_uni_map

    def get_courses_to_take(self, uni_to_cc_map):
        """Extract the set of all community college courses needed for transfer."""
        cc_courses_to_take = set()
        for cc_list in uni_to_cc_map.values():
            for cc in cc_list:
                cc_courses_to_take.add(cc)
        
        return cc_courses_to_take
    
    def map_alternatives_cc_classes(self, uni_to_cc_map):
        """Map university courses to their alternative CC courses."""
        uni_course_alternatives = {}
        for uni_course, cc_courses in uni_to_cc_map.items():
            uni_course_alternatives[uni_course] = cc_courses
        
        return uni_course_alternatives
