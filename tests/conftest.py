import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_db():
    """Return a simple mocked database session."""
    db = MagicMock()
    return db

@pytest.fixture
def patch_get_vector_db(mock_db):
    with patch('app.db.connection.get_vector_db', return_value=mock_db):
        yield mock_db
