from app.db.connection import get_db
import pytest

@pytest.fixture
def db():
    connection = get_db()
    try:
        yield connection
    finally:
        connection.close()
