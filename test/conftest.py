from app.db.connection import get_vector_db
import pytest

@pytest.fixture
def db():
    connection = get_vector_db()
    try:
        yield connection
    finally:
        connection.close()
