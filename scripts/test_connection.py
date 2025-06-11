import sys
import os

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from sqlalchemy import text

def main():
    db = get_vector_db()
    try:
        print("Testing connection...")
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"Connection successful: {result}")
        
        # Check if PostgreSQL version supports pgvector
        version = db.execute(text("SELECT version()")).fetchone()[0]
        print(f"PostgreSQL version: {version}")
        
        # List available extensions
        extensions = db.execute(text("SELECT * FROM pg_available_extensions")).fetchall()
        print("Available extensions:")
        for ext in extensions:
            print(f"  {ext.name}: {ext.default_version}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()