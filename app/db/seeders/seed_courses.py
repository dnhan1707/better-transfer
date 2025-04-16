import os
import json
from sqlalchemy.orm import Session
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges

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

        # Get colleges lookup table
        colleges = {college.college_name: college.id for college in db.query(Colleges).all()}
        
        for course_data in courses_data:
            # Extract college name and look up ID
            college_name = course_data.pop("college_name")
            if college_name not in colleges:
                print(f"Warning: College '{college_name}' not found, skipping course")
                continue
                
            # Create course with college ID
            course = Courses(
                code=course_data["code"],
                name=course_data["name"],
                units=course_data["units"],
                difficulty=course_data["difficulty"],
                college_id=colleges[college_name]
            )
            db.add(course)
        
        db.commit()
        print(f"Successfully seeded {len(courses_data)} courses")
    except Exception as e:
        db.rollback()
        print(f"Error seeding courses: {str(e)}")