import pytest
from unittest.mock import MagicMock
from RAG.services.knowledge_chunker import KnowledgeChunker
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges
from app.db.models.prerequisites import Prerequisites

@pytest.fixture
def db_mock():
    """Create a mock database with sample query results."""
    db = MagicMock()
    
    # Mock course data
    mock_course = MagicMock(spec=Courses)
    mock_course.code = "CS101"
    mock_course.name = "Intro to CS"
    mock_course.units = 3.0
    mock_course.difficulty = 5
    
    mock_college = MagicMock(spec=Colleges)
    mock_college.id = 1
    mock_college.college_name = "Test College"
    
    db.query.return_value.join.return_value.all.return_value = [(mock_course, mock_college)]
    
    return db

@pytest.mark.asyncio
async def test_generate_course_chunker(db_mock):
    """Test course chunking functionality."""
    chunker = KnowledgeChunker()
    chunks = await chunker.generate_course_chunker(db_mock)
    
    assert len(chunks) == 1
    assert "CS101 (Intro to CS)" in chunks[0]["content"]
    assert chunks[0]["college_id"] == 1
    assert chunks[0]["college_name"] == "Test College"
    assert chunks[0]["chunk_type"] == "course_description"