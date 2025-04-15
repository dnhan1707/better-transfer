import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import SessionLocal
from app.db.seeders.seed_runner import run_all_seeder

def main():
    """Main function to seed the database"""
    db = SessionLocal()
    try:
        run_all_seeder(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()