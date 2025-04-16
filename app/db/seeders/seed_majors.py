import os
import json
from sqlalchemy.orm import Session
from app.db.models.majors import Majors
from app.db.models.universities import Universities

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

        # Get universities lookup table
        universities = {uni.university_name: uni.id for uni in db.query(Universities).all()}
        
        for major_data in majors_data:
            # Extract university name and look up ID
            university_name = major_data.pop("university_name")
            if university_name not in universities:
                print(f"Warning: University '{university_name}' not found, skipping major")
                continue
                
            # Create major with university ID
            major = Majors(
                major_name=major_data["major_name"],
                university_id=universities[university_name]
            )
            db.add(major)
        
        db.commit()
        print(f"Successfully seeded {len(majors_data)} majors")
    except Exception as e:
        db.rollback()
        print(f"Error seeding majors: {str(e)}")