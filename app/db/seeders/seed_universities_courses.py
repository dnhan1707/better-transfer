import os
import json
from sqlalchemy.orm import Session
from app.db.models.university_courses import UniversityCourses
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.course_major_mapping import CourseMajorMapping
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def seed_universities_courses(db: Session):
    data_count = db.query(UniversityCourses).count()
    if(data_count > 0):
        logger.info(f"Skipping seed UniversityCourses, {data_count} found in the model")
        return
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "universities_courses.json")
        
        with open(file_path, "r") as file:
            universities_courses_data = json.load(file)

        # Get universities lookup table
        universities = {uni.university_name: uni.id for uni in db.query(Universities).all()}
        
        # Get majors lookup table
        majors = {}
        for major in db.query(Majors).all():
            key = f"{major.major_name}_{major.university_id}"
            majors[key] = major.id
        
        for course_data in universities_courses_data:
            # Skip if no university name
            if "university_name" not in course_data:
                logger.warning("Missing university_name in course data, skipping")
                continue
                
            # Extract university name
            university_name = course_data["university_name"]
            if university_name not in universities:
                logger.warning(f"University '{university_name}' not found, skipping")
                continue
                
            # Get university ID
            university_id = universities[university_name]
            
            # Create university course (without major_id)
            university_course = UniversityCourses(
                course_name=course_data["course_name"],
                course_code=course_data["course_code"],
                university_id=university_id  # Only set university_id
            )
            db.add(university_course)
            db.flush()  # Get the newly created ID
            
            # Create mapping for each major in the majors array
            if "majors" in course_data and isinstance(course_data["majors"], list):
                for major_name in course_data["majors"]:
                    major_key = f"{major_name}_{university_id}"
                    if major_key in majors:
                        # Create mapping in the junction table
                        mapping = CourseMajorMapping(
                            university_course_id=university_course.id,
                            major_id=majors[major_key]
                        )
                        db.add(mapping)
                    else:
                        logger.warning(f"Major '{major_name}' at '{university_name}' not found")
            else:
                logger.warning(f"Missing or invalid majors array for {course_data['course_name']}")
        
        db.commit()
        logger.info(f"Successfully seeded university courses with major mappings")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding university courses: {str(e)}")