import pytest
from unittest.mock import MagicMock

@pytest.fixture
def db():
    """Return a mocked database session."""
    db = MagicMock()
    return db
