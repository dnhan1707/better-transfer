import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from app.services.prerequisite_graph import build_prerequisite_graph

def main():
    """Main function to seed the database"""
    db = SessionLocal()
    try:
        result = build_prerequisite_graph(db, 1)
        if isinstance(result, tuple) and len(result) == 2:
            prerequisite_graph, leads_to = result
            print(prerequisite_graph)
            print("======================================")
            print(leads_to)
        else:
            print("Error: build_prerequisite_graph did not return a tuple of length 2.")
    finally:
        db.close()

if __name__ == "__main__":
    main()