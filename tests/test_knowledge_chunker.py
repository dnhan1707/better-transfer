import pytest
from unittest.mock import MagicMock
from RAG.services.knowledge_chunker import KnowledgeChunker
from app.db.models.courses import Courses
from app.db.models.colleges import Colleges

@pytest.fixture
def db_mock():
    db = MagicMock()
    course = MagicMock(spec=Courses)
    course.code = "CS101"
    course.name = "Intro"
    course.units = 3
    course.difficulty = 5

    college = MagicMock(spec=Colleges)
    college.id = 1
    college.college_name = "Test College"

    db.query.return_value.join.return_value.all.return_value = [(course, college)]
    return db

@pytest.mark.asyncio
async def test_generate_course_chunker(db_mock):
    chunker = KnowledgeChunker()
    chunks = await chunker.generate_course_chunker(db_mock)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["college_id"] == 1
    assert chunk["chunk_type"] == "course_description"
