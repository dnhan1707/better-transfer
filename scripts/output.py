import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from app.services.prerequisite_graph import build_prerequisite_graph, plan_course_sequence, topological_sort

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
        
        else:
            print("Error: build_prerequisite_graph did not return a tuple of length 2.")
    finally:
        db.close()

if __name__ == "__main__":
    main()