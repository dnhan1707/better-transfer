from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")

app_engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
vector_engine = create_engine(RAG_DATABASE_URL, pool_pre_ping=True, future=True)

AppSession = sessionmaker(bind=app_engine,     autoflush=False, autocommit=False, expire_on_commit=False)
VectorSession = sessionmaker(bind=vector_engine,  autoflush=False, autocommit=False, expire_on_commit=False)

Base = declarative_base()

def get_db():
    db: Session = AppSession()
    try:
        yield db               # hand it to FastAPI
    finally:
        db.close()             # close *after* the request

def get_vector_db():
    db: Session = VectorSession()
    try:
        yield db
    finally:
        db.close()
