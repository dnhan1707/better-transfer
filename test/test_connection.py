from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pytest

def test_db_connection(db):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1

    except SQLAlchemyError as e:
        pytest.fail(f"Database connection failed: {e}")


def test_pgvector_extension_available(db):
    extensions = db.execute(text("SELECT name FROM pg_available_extensions WHERE name='vector'")).fetchall()
    assert any(ext[0] == 'vector' for ext in extensions), "pgvector extension is not available"
