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
        current_dir = os.path(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "articulation_group.json")

        with open(file_path, "r") as file:
            articulation_group = json.load(file)


        for group in articulation_group:
            id = group.id
            university_list = group.ununiversity_courses
            operator = group.operator
            major = group.major_name
            uni_name = group.university_name

            

    except Exception as e:
        db.rollback()
        print(f"Error seeding articulation group {str(e)}")
