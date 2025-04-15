import os
import json
from sqlalchemy.orm import Session
from app.db.models.majors import Majors


def seed_majors(db: Session):
    data_count = db.query(Majors).count()
    if(data_count > 0):
        print(f"Skipping seed majors, {data_count} found in the model")
        return
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "majors.json")
        
        with open(file_path, "r") as file:
            majors_data = json.load(file)

        for major_data in majors_data:
            major = Majors(**major_data)
            db.add(major)
        
        db.commit()
        print(f"Successfully seeded {len(majors_data)} majors")
    except Exception as e:
        db.rollback()
        print(f"Error seeding majors: {str(e)}")

