import pytest
import asyncio
from unittest.mock import MagicMock, patch
from RAG.db.vector_store import VectorStore
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
    await vector_store.create_vector_table(db=db_mock)

    db_mock.execute.assert_called_once()
    db_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_insert_chunk(db_mock):
    vector_store = VectorStore()

    chunk = {
        "content": "Test content",
        "college_id": 1,
        "college_name": "Test College"
    }
    embedding = [0.1] * 1536  # 1536 dimensions
    await vector_store.insert_chunk(db=db_mock, chunk=chunk, embedding=embedding)

    db_mock.execute.assert_called_once()
    db_mock.commit.assert_called_once()



@pytest.mark.asyncio
async def test_vector_search(db_mock):
    vector_store = VectorStore()
    
    # Create a more sophisticated mock to handle multiple calls
    mock = MagicMock()
    first_call = MagicMock()
    first_call.fetchall.return_value = [(1, "content1", "college1", "uni1", "major1", "course_des1", 0.9)]
    
    second_call = MagicMock()
    second_call.fetchall.return_value = []  # Empty for second query
    
    # Setup the mock to return different values on subsequent calls
    db_mock.execute.side_effect = [first_call, second_call]

    with patch("RAG.services.embedding_services.EmbeddingService.create_embedding",
               return_value=[0.1]*1536):
        request = TransferPlanRequest(college_id=1, university_id=1, major_id=1)
        results = await vector_store.vector_search(db_mock, "test query", request)
        
        assert len(results) == 1
        assert results[0]["content"] == "content1"
        assert results[0]["similarity"] == 0.9
        assert results[0]["chunk_type"] == "course_des1"