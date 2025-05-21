import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models explicitly to avoid circular dependency issues
from app.db.models.universities import Universities
from app.db.models.colleges import Colleges
from app.db.models.majors import Majors
from app.db.models.courses import Courses
from app.db.models.prerequisites import Prerequisites
from app.db.models.university_courses import UniversityCourses
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.expression_node import ExpressionNode, NodeType, OperatorType
from app.db.models.articulation_group import ArticulationGroup

from app.db.connection import SessionLocal
from app.services.prerequisite_graph import build_prerequisite_graph, plan_course_sequence, topological_sort
from app.services.transfer_service import create_transfer_plan

# Rest of your main function remains the same
def main():
    """Main function to seed the database"""
    db = SessionLocal()
    try:
        result = build_prerequisite_graph(db, 1)
        if isinstance(result, tuple) and len(result) == 2:
            prerequisite_graph, leads_to = result
            print("==========PREREQUISITE GRAPH=============")
            print(prerequisite_graph)
            print("==========LEADS TO GRAPH==========")
            print(leads_to)
            print("==========TOPOLOGICAL SORT==============")
            sorted_course = topological_sort(prerequisite_graph)
            print(sorted_course)
            print("==========TRANSFER PLAN==============")

            planned_course = plan_course_sequence(sorted_course, 4, prerequisite_graph)
            print(planned_course)
            print("==========TRANSFER PLAN V.2==============")

            plan = create_transfer_plan(db, 1, 1, 1, num_of_terms=6)
            print(plan)
        
        else:
            print("Error: build_prerequisite_graph did not return a tuple of length 2.")
    finally:
        db.close()

if __name__ == "__main__":
    main()