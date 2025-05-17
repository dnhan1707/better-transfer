import os
import json
from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements
from app.db.models.articulation_group import ArticulationGroup
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.db.models.universities import Universities
from app.db.models.majors import Majors
from app.db.models.university_courses import UniversityCourses


def seed_articulation_group(db: Session):
    data_count = db.query(ArticulationGroup).count()
    if(data_count > 0):
        print(f"Skipping seed articulations, {data_count} found in the model")
        return

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "articulation_group.json")

        with open(file_path, "r") as file:
            articulation_groups = json.load(file)


        for group in articulation_groups:
            university = db.query(Universities).filter(
                Universities.university_name == group["university_name"]
            ).first()
            if not university:
                print(f"University not found: {group['university_name']}")
                continue

            major = db.query(Majors).filter(
                Majors.major_name == group["major_name"],
                Majors.university_id == university.id
            ).first()
            if not major:
                print(f"Major not found: {group['major_name']} at {group['university_name']}")
                continue
            
            college = db.query(Colleges).filter(
                Colleges.college_name == group["college_name"]
            ).first()
            if not college:
                print(f"College not found: {group['college_name']}")
                continue
            
            new_group = ArticulationGroup(
                university_id=university.id,
                major_id = major.id,
                college_id = college.id,
                expression = group["expression"]
            )

            db.add(new_group)

        db.commit()
        print(f"Successfully seeded {len(articulation_groups)} articulation groups")


    except Exception as e:
        db.rollback()
        print(f"Error seeding articulation group {str(e)}")
