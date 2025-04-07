from app.db.connection import Base
import app.db.models  # This imports all models via __init__.py

print("Registered tables:", Base.metadata.tables.keys())