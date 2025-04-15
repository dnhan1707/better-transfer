import os
import json
from sqlalchemy.orm import Session
from app.db.models.courses import Courses


def seed_courses(db: Session):
    data_count = db.query(Courses).count()
    if(data_count > 0):
        print(f"Skipping seed Courses, {data_count} found in the model")
        return
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "courses.json")
        
        with open(file_path, "r") as file:
            courses_data = json.load(file)

        for courses in courses_data:
            course = Courses(**courses)
            db.add(course)
        
        db.commit()
        print(f"Successfully seeded {len(courses)} courses")
    except Exception as e:
        db.rollback()
        print(f"Error seeding UniversityCourses: {str(e)}")

