from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.connection import get_db


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to Better Transfer API"}


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful"}

    except Exception as e:
        return {"error": str(e)}
