import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import app_engine, Base
from app.db.models import * # Import all your models here

def main():
    """Create all database tables based on SQLAlchemy models"""
    print("Creating database schema...")
    Base.metadata.create_all(bind=app_engine)
    print("Schema created successfully!")

if __name__ == "__main__":
    main()