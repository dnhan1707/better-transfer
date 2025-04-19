import os
import json
from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.university_courses import UniversityCourses

def seed_articulations(db: Session):
    data_count = db.query(ArticulationAgreements).count()
    if(data_count > 0):
        print(f"Skipping seed articulations, {data_count} found in the model")
        return
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "articulations.json")
        
        with open(file_path, "r") as file:
            articulations_data = json.load(file)

        # Lookup tables
        colleges = {c.college_name: c.id for c in db.query(Colleges).all()}
        universities = {u.university_name: u.id for u in db.query(Universities).all()}
        
        # More complex lookups
        courses_map = {}
        for course in db.query(Courses).all():
            college = db.query(Colleges).filter(Colleges.id == course.college_id).first()
            if college:
                key = f"{college.college_name}_{course.code}"
                courses_map[key] = course.id
                
        majors_map = {}
        for major in db.query(Majors).all():
            university = db.query(Universities).filter(Universities.id == major.university_id).first()
            if university:
                key = f"{university.university_name}_{major.major_name}"
                majors_map[key] = major.id
                
        uni_courses_map = {}
        for uni_course in db.query(UniversityCourses).all():
            # Get the university directly
            university = db.query(Universities).filter(Universities.id == uni_course.university_id).first()
            if not university:
                continue
                
            # For each university course, get the associated majors through the mapping table
            for mapping in uni_course.major_mappings:
                major = mapping.major
                if major:
                    # Create a key for each university-major-course combination
                    key = f"{university.university_name}_{major.major_name}_{uni_course.course_code}"
                    uni_courses_map[key] = uni_course.id
                    
        # Create articulations
        successful_count = 0
        for item in articulations_data:
            # Extract data
            cc_name = item["community_college"]["college_name"]
            cc_code = item["community_college"]["course_code"]
            uni_name = item["university"]["university_name"] 
            major_name = item["university"]["major_name"]
            uni_code = item["university"]["course_code"]
            
            # Look up IDs
            cc_course_key = f"{cc_name}_{cc_code}"
            uni_key = uni_name
            major_key = f"{uni_name}_{major_name}"
            uni_course_key = f"{uni_name}_{major_name}_{uni_code}"
            
            # Skip if any component is missing
            if cc_course_key not in courses_map:
                print(f"Warning: Community college course {cc_code} at {cc_name} not found")
                continue
                
            if uni_key not in universities:
                print(f"Warning: University {uni_name} not found")
                continue
                
            if major_key not in majors_map:
                print(f"Warning: Major {major_name} at {uni_name} not found")
                continue
                
            if uni_course_key not in uni_courses_map:
                print(f"Warning: University course {uni_code} for {major_name} at {uni_name} not found")
                continue
                
            # Create the articulation
            articulation = ArticulationAgreements(
                community_college_course_id=courses_map[cc_course_key],
                university_course_id=uni_courses_map[uni_course_key],
                university_id=universities[uni_key],
                major_id=majors_map[major_key]
            )
            db.add(articulation)
            successful_count += 1
        
        db.commit()
        print(f"Successfully seeded {successful_count} articulation agreements")
    except Exception as e:
        db.rollback()
        print(f"Error seeding articulations: {str(e)}")