from app.db.crud.articulations import db_get_prerequisite_relationships_for_college
from sqlalchemy.orm import Session

'''
SORT by Prerequisite

Data Structure: Directed Acyclic Graph
'''

def build_prerequisite_graph(db: Session, college_id: int):
    prerequisite_relationships = db_get_prerequisite_relationships_for_college(db, college_id)
    prerequisite_graph = {} # course -> prerequisites
    leads_to = {}  # prerequisite -> courses allowed to takes after

    for rel in prerequisite_relationships:
        if(rel.course_code not in prerequisite_graph):
            prerequisite_graph[rel.course_code] = []
        prerequisite_graph[rel.course_code].append({
            "code": rel.prerequisite_code,
            "type": rel.prerequisite_type
        })

        if(rel.prerequisite_code not in leads_to):
            prerequisite_graph[rel.prerequisite_code] = []
        prerequisite_graph[rel.course_code].append({
            "code": rel.course_code,
            "type": rel.prerequisite_type
        })

    return prerequisite_graph, leads_to
