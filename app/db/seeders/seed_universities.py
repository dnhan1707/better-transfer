import os
import json
from sqlalchemy.orm import Session
from app.db.models.universities import Universities


def seed_universities(db: Session):
    data_count = db.query(Universities).count()
    if(data_count > 0):
        print(f"Skipping seed universities, {data_count} found in the model")
        return
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "universities.json")
        
        with open(file_path, "r") as file:
            universities_data = json.load(file)

        for university_data in universities_data:
            universities = Universities(**university_data)
            db.add(universities)
        
        db.commit()
        print(f"Successfully seeded {len(universities_data)} universities")
    except Exception as e:
        db.rollback()
        print(f"Error seeding universitites: {str(e)}")

