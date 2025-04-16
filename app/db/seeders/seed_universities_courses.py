import os
import json
from sqlalchemy.orm import Session
from app.db.models.university_courses import UniversityCourses
from app.db.models.universities import Universities
from app.db.models.majors import Majors

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

        # Get universities lookup table
        universities = {uni.university_name: uni.id for uni in db.query(Universities).all()}
        
        # Get majors lookup table (need to include university_id to handle same major name at different universities)
        majors = {}
        for major in db.query(Majors).all():
            key = f"{major.major_name}_{major.university_id}"
            majors[key] = major.id
        
        for course_data in universities_courses_data:
            # Extract university and major names
            university_name = course_data.pop("university_name")
            major_name = course_data.pop("major_name")
            
            if university_name not in universities:
                print(f"Warning: University '{university_name}' not found, skipping course")
                continue
                
            university_id = universities[university_name]
            major_key = f"{major_name}_{university_id}"
            
            if major_key not in majors:
                print(f"Warning: Major '{major_name}' at '{university_name}' not found, skipping course")
                continue
                
            # Create university course with major ID
            university_course = UniversityCourses(
                course_name=course_data["course_name"],
                course_code=course_data["course_code"],
                major_id=majors[major_key]
            )
            db.add(university_course)
        
        db.commit()
        print(f"Successfully seeded {len(universities_courses_data)} university courses")
    except Exception as e:
        db.rollback()
        print(f"Error seeding university courses: {str(e)}")