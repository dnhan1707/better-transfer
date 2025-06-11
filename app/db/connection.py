from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Application database
DATABASE_URL = os.getenv("DATABASE_URL")
app_engine = create_engine(DATABASE_URL)
AppSession = sessionmaker(autocommit=False, autoflush=False, bind=app_engine)
SessionLocal = AppSession

# Vector database for RAG
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")
vector_engine = create_engine(RAG_DATABASE_URL)
VectorSession = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)
Base = declarative_base()


def get_db():
    db = AppSession()
    try:
        return db
    finally:
        db.close()

def get_vector_db():
    db = VectorSession()
    try:
        return db
    finally:
        db.close()