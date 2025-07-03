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
    
    # Create mocks for SQL query results
    # First query - specific chunks for university1-major1
    first_query = MagicMock()
    first_query.fetchall.return_value = [
        (1, "articulation1", "college1", "university1", "major1", "articulation", 0.95)
    ]
    
    # Second query - specific chunks for university2-major2
    second_query = MagicMock()
    second_query.fetchall.return_value = [
        (2, "articulation2", "college1", "university2", "major2", "articulation", 0.92)
    ]
    
    # Third query - general course information
    third_query = MagicMock()
    third_query.fetchall.return_value = [
        (3, "course_info", "college1", None, None, "class", 0.85)
    ]
    
    # Set up the mock to return different results for each execute call
    db_mock.execute.side_effect = [first_query, second_query, third_query]

    # Create target combinations list with multiple targets
    target_combinations = [
        {
            "college": "college1",
            "university": "university1", 
            "major": "major1"
        },
        {
            "college": "college1",
            "university": "university2", 
            "major": "major2"
        }
    ]

    # Mock the embedding service
    with patch("RAG.services.embedding_services.EmbeddingService.create_embedding",
              return_value=[0.1]*1536):
        results = await vector_store.vector_search_v2(db_mock, "test query", target_combinations)
        
        # Verify results
        assert len(results) == 3
        assert results[0]["content"] == "articulation1"
        assert results[0]["university_name"] == "university1"
        assert results[0]["major_name"] == "major1"
        
        assert results[1]["content"] == "articulation2"
        assert results[1]["university_name"] == "university2"
        assert results[1]["major_name"] == "major2"
        
        assert results[2]["content"] == "course_info"
        assert results[2]["chunk_type"] == "class"
        
        # Verify the SQL queries were executed the expected number of times
        assert db_mock.execute.call_count == 3