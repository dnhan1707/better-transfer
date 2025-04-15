import os
import json
from sqlalchemy.orm import Session
from app.db.models.colleges import Colleges


def seed_colleges(db: Session):
    # Check if colleges already exist
    data_count = db.query(Colleges).count()
    if(data_count > 0):
        print(f"Skipping colleges seeding, {data_count} already exist in Colleges model")
        return
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "colleges.json")
        with open(file_path, "r") as file:
            colleges_data = json.load(file)

        # Insert
        for college_data in colleges_data:
            college = Colleges(**college_data)
            db.add(college)
        
        db.commit()
        print(f"Successfully seeded {len(colleges_data)} colleges")

    except Exception as e:
        db.rollback()
        print(f"Error seeding colleges: {str(e)}")
