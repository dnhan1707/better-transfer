from app.db.crud.articulations import db_get_prerequisite_relationships_for_college
from sqlalchemy.orm import Session

'''
SORT by Prerequisite

Data Structure: Directed Acyclic Graph
'''

def build_prerequisite_graph(db: Session, college_id: int):
    prerequisite_relationships = db_get_prerequisite_relationships_for_college(db, college_id)
    prerequisite_graph = {}  # course -> prerequisites
    leads_to = {}  # prerequisite -> courses allowed to take after

    for rel in prerequisite_relationships:
        # Add to prerequisite graph
        if rel.course_code not in prerequisite_graph:
            prerequisite_graph[rel.course_code] = []
        prerequisite_graph[rel.course_code].append({
            "code": rel.prerequisite_code,
            "type": rel.prerequisite_type
        })

        # Add to leads_to graph 
        if rel.prerequisite_code not in leads_to:
            leads_to[rel.prerequisite_code] = []
        leads_to[rel.prerequisite_code].append({
            "code": rel.course_code,
            "type": rel.prerequisite_type
        })

    return prerequisite_graph, leads_to

def topological_sort(prerequisite_graph):
    # Make sure the prerequisite courses come first
    visited = set()
    temp_visited = set()
    res = []

    def visit(course):
        if course in temp_visited:
            raise ValueError(f"Cycle detected in prerequisites involving {course}")
        if course not in visited:
            temp_visited.add(course)

            prerequisites = [p["code"] for p in prerequisite_graph.get(course, [])]
            for prere in prerequisites:
                visit(prere)
            
            temp_visited.remove(course)
            visited.add(course)
            res.append(course)

    for course in prerequisite_graph:
        if course not in visited:
            visit(course)
    
    return res

def plan_course_sequence(sorted_course, max_classes_per_term):
    # Group courses into balanced terms
    # Somehow ensure prioritize that same type of courses are in different terms
    pass
