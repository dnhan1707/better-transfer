import os
import json
import uuid
from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements, ArticulationRelationshipType
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.university_courses import UniversityCourses
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def seed_articulations(db: Session):
    data_count = db.query(ArticulationAgreements).count()
    if(data_count > 0):
        logger.info(f"Skipping seed articulations, {data_count} found in the model")
        return
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "articulations.json")
        
        with open(file_path, "r") as file:
            articulations_data = json.load(file)

        # Lookup tables
        colleges = {c.college_name: c.id for c in db.query(Colleges).all()}
        universities = {u.university_name: u.id for u in db.query(Universities).all()}
        
        # Course lookup map
        courses_map = {}
        for course in db.query(Courses).all():
            college = db.query(Colleges).filter(Colleges.id == course.college_id).first()
            if college:
                key = f"{college.college_name}_{course.code}"
                courses_map[key] = course.id
                
        # Majors lookup map
        majors_map = {}
        for major in db.query(Majors).all():
            university = db.query(Universities).filter(Universities.id == major.university_id).first()
            if university:
                key = f"{university.university_name}_{major.major_name}"
                majors_map[key] = major.id
                
        # University courses lookup map
        uni_courses_map = {}
        for uni_course in db.query(UniversityCourses).all():
            university = db.query(Universities).filter(Universities.id == uni_course.university_id).first()
            if not university:
                continue
                
            key = f"{university.university_name}_{uni_course.course_code}"
            uni_courses_map[key] = uni_course.id
        
        # Create articulations
        successful_count = 0
        
        for item in articulations_data:
            # Extract data
            uni_name = item["university_name"]
            cc_name = item["college"]
            major_name = item["major_name"]
            uni_course_code = item["university_course"]
            relationship_type_str = item["relationship_type"]
            cc_courses = item["community_college_courses"]
            
            # Look up IDs
            if uni_name not in universities:
                logger.warning(f"University {uni_name} not found")
                continue
                
            uni_id = universities[uni_name]
            
            major_key = f"{uni_name}_{major_name}"
            if major_key not in majors_map:
                logger.warning(f"Major {major_name} at {uni_name} not found")
                continue
                
            major_id = majors_map[major_key]
            
            uni_course_key = f"{uni_name}_{uni_course_code}"
            if uni_course_key not in uni_courses_map:
                logger.warning(f"University course {uni_course_code} at {uni_name} not found")
                continue
                
            uni_course_id = uni_courses_map[uni_course_key]
            
            # Determine relationship type
            relationship_type = ArticulationRelationshipType.OR
            if relationship_type_str == "AND":
                relationship_type = ArticulationRelationshipType.AND
            
            # Generate a unique group ID for this set of articulations
            group_id = f"{uni_name}_{uni_course_code}_{uuid.uuid4().hex[:8]}"
            
            # Process each community college course
            for cc_course_info in cc_courses:
                cc_code = cc_course_info["code"]
                cc_course_key = f"{cc_name}_{cc_code}"
                
                if cc_course_key not in courses_map:
                    logger.warning(f"Community college course {cc_code} at {cc_name} not found")
                    continue
                
                cc_course_id = courses_map[cc_course_key]
                
                # Create the articulation
                articulation = ArticulationAgreements(
                    community_college_course_id=cc_course_id,
                    university_course_id=uni_course_id,
                    university_id=uni_id,
                    major_id=major_id,
                    group_id=group_id,
                    relationship_type=relationship_type
                )
                db.add(articulation)
                successful_count += 1
        
        db.commit()
        logger.info(f"Successfully seeded {successful_count} articulation agreements")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding articulations: {str(e)}")
        raise e  # Re-raise to see the full traceback