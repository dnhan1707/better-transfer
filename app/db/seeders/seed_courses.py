import os
import json
from sqlalchemy.orm import Session
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def seed_courses(db: Session):
    data_count = db.query(Courses).count()
    if(data_count > 0):
        logger.info(f"Skipping seed Courses, {data_count} found in the model")
        return

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "courses.json")
        
        with open(file_path, "r") as file:
            courses_data = json.load(file)

        colleges = {}
        # Create a colleges lookup table (Like a map, key is college name value is id)
        for college in db.query(Colleges).all():
            colleges[college.college_name] = college.id
        
        # Add courses into the Courses table
        for course_data in courses_data:
            # Extract college name and look up Id
            college_name = course_data.pop("college_name")
            if(college_name not in colleges):
                logger.warning(f"College '{college_name}' not found, skipping course")
                continue

            # Create course with that Id to add into the table
            course = Courses(
                code = course_data["code"],
                name=course_data["name"],
                units=course_data["units"],
                difficulty=course_data["difficulty"],
                college_id=colleges[college_name]
            )
            db.add(course)
            
        db.commit()
        logger.info(f"Successfully seeded {len(courses_data)} courses")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding courses: {str(e)}")