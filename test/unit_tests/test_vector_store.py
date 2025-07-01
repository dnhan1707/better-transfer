import pytest
from unittest.mock import MagicMock, patch
from RAG.db.vector_store import VectorStore
from RAG.services.chunker_service import ChunkerService
from app.schemas.transferPlanRequest import TransferPlanRequest


@pytest.fixture
def db_mock():
    # This create a mock database (or a fake db)
    mock = MagicMock()
    mock.execute.return_value.fetchall.return_value = []
    return mock


@pytest.mark.asyncio
async def test_create_vector_table(db_mock):
    vector_store = VectorStore()
    await vector_store.create_vector_table_v2(vector_db=db_mock)

    db_mock.execute.assert_called_once()
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_insert_chunk(db_mock):
    service = ChunkerService()

    chunk = {
        "content": "Test content",
        "college_id": 1,
        "college_name": "Test College",
        "chunk_type": "Test chunk type"
    }
    embedding = [0.1] * 1536  # 1536 dimensions
    await service.insert_chunk(db=db_mock, chunk=chunk, embedding=embedding)

    db_mock.execute.assert_called_once()
    db_mock.commit.assert_called_once()



@pytest.mark.asyncio
async def test_vector_search(db_mock):
    vector_store = VectorStore()
    
    # Create mocks for first and second DB queries
    first_call = MagicMock()
    first_call.fetchall.return_value = [(1, "content1", "college1", "uni1", "major1", "course_des1", 0.9)]
    second_call = MagicMock()
    second_call.fetchall.return_value = []
    db_mock.execute.side_effect = [first_call, second_call]

    # Create mock college, university and major objects
    mock_college = MagicMock()
    mock_college.college_name = "Test College"
    
    mock_university = MagicMock()
    mock_university.university_name = "Test University"
    
    mock_major = MagicMock()
    mock_major.major_name = "Test Major"
    
    # Create the expected basic_info structure
    basic_info = {
        "college": mock_college,
        "university": mock_university,
        "major": mock_major
    }

    with patch("RAG.services.embedding_services.EmbeddingService.create_embedding",
               return_value=[0.1]*1536):
        results = await vector_store.vector_search_v2(db_mock, "test query", basic_info)
        
        assert len(results) == 1
        assert results[0]["content"] == "content1"