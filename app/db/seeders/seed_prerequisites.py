import os
import json
from sqlalchemy.orm import Session
from app.db.models.prerequisites import Prerequisites
from app.db.models.courses import Courses
from app.db.models.prerequisites import PrerequisiteType


def seed_prerequisite(db: Session):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "prerequisite.json")

        with open(file_path, "r") as file:
            prerequisite_data = json.load(file)
        
        for prereq in prerequisite_data: 
            course = db.query(Courses).filter(
                Courses.code == prereq["course_code"],
                Courses.college_id == prereq["college_id"]
            ).first()

            prerequisite_course = db.query(Courses).filter(
                Courses.code == prereq["prerequisite_course_code"],
                Courses.college_id == prereq["college_id"]
            ).first()
            
            if not course or not prerequisite_course:
                print(f"Warning: Could not find course for {prereq}")
                continue
            
            # Create prerequisite relationship
            db.add(Prerequisites(
                course_id=course.id,
                prerequisite_course_id=prerequisite_course.id,
                prerequisite_type=PrerequisiteType(prereq["prerequisite_type"])
            ))
        
        db.commit()
        print(f"Seeded {len(prerequisite_data)} prerequisites")
    except Exception as e:
        db.rollback()
        print(f"Error seeding prerequisite: {str(e)}")
