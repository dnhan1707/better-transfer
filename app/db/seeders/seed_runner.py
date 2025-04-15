from sqlalchemy.orm import Session
from app.db.seeders.seed_colleges import seed_colleges


def run_all_seeder(db: Session):
    """Run all seeders in the correct order based on dependencies"""
    print("Starting database seeding process...")
    
    # Run seeders in order of dependencies
    seed_colleges(db)
    
    print("Database seeding complete!")
