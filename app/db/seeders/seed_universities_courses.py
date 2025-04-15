import os
import json
from sqlalchemy.orm import Session
from app.db.models.university_courses import UniversityCourses


def seed_universities_courses(db: Session):
    data_count = db.query(UniversityCourses).count()
    if(data_count > 0):
        print(f"Skipping seed UniversityCourses, {data_count} found in the model")
        return
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "universities_courses.json")
        
        with open(file_path, "r") as file:
            universities_courses_data = json.load(file)

        for universities_courses in universities_courses_data:
            universities_course = UniversityCourses(**universities_courses)
            db.add(universities_course)
        
        db.commit()
        print(f"Successfully seeded {len(universities_courses)} UniversityCourses")
    except Exception as e:
        db.rollback()
        print(f"Error seeding UniversityCourses: {str(e)}")

