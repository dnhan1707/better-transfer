import pytest
from unittest.mock import patch, MagicMock
from RAG.services.embedding_services import EmbeddingService


class MockResponse:
    def __init__(self, embedding):
        self.data = [MagicMock(embedding=embedding)]

@pytest.mark.asyncio
async def test_create_embedding():
    mock_result = [0.1] * 1536

    with patch("openai.embeddings.create",
               return_value=MockResponse(mock_result)):
        embedding_service = EmbeddingService()
        embedding = await embedding_service.create_embedding(texts="test")

        assert embedding == mock_result

        
@pytest.mark.asyncio
async def test_batch_create_embedding():
    """Test creating batch embeddings."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536]
    
    # Create a response with multiple data items
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=mock_embeddings[0]),
        MagicMock(embedding=mock_embeddings[1])
    ]
    
    with patch("openai.embeddings.create", return_value=mock_response):
        embedding_service = EmbeddingService()
        result = await embedding_service.batch_create_embedding(["text1", "text2"])
        
        assert len(result) == 2
        assert result[0] == mock_embeddings[0]
        assert result[1] == mock_embeddings[1]