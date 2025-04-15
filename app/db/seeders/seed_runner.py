from sqlalchemy.orm import Session
from app.db.seeders.seed_colleges import seed_colleges
from app.db.seeders.seed_universities import seed_universities
from app.db.seeders.seed_courses import seed_courses
from app.db.seeders.seed_majors import seed_majors
from app.db.seeders.seed_universities_courses import seed_universities_courses
from app.db.seeders.seed_articulations import seed_articulations


def run_all_seeder(db: Session):
    """Run all seeders in the correct order based on dependencies"""
    print("Starting database seeding process...")
    
    # Run seeders in correct dependency order
    # seed_colleges(db)
    # seed_universities(db)
    # seed_majors(db)       
    # seed_courses(db)      
    # seed_universities_courses(db)  
    # seed_articulations(db)  
    
    # print("Database seeding complete!")
    print("Database is fully added")