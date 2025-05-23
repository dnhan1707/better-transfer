import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from app.services.transfer_service import TransferPlanService

def main():
    """Main function to seed the database"""
    db = SessionLocal()
    try:
        plan = TransferPlanService.create_transfer_plan(db, 1, 1, 1, num_of_terms=4)
        print(plan)
    
    finally:
        db.close()

if __name__ == "__main__":
    main()