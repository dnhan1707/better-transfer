import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from RAG.services.embedding_services import EmbeddingService
from RAG.services.caching_service import CachingService


class MockResponse:
    def __init__(self, embedding):
        self.data = [MagicMock(embedding=embedding)]


@pytest.mark.asyncio
async def test_create_embedding_no_db():
    """Test creating single embedding without database (no caching)."""
    mock_result = [0.1] * 1536

    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock(return_value=MockResponse(mock_result))
    
    # Call without db parameter
    embedding = await embedding_service.create_embedding(text="test", db=None)
    
    # Verify result and API call
    assert embedding == mock_result
    embedding_service.client.embeddings.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_embedding_with_cache_miss():
    """Test creating single embedding with database but cache miss."""
    mock_result = [0.1] * 1536
    mock_db = MagicMock()

    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock(return_value=MockResponse(mock_result))
    
    # Mock cache miss
    embedding_service.caching_service.get_cached_embedding = AsyncMock(return_value=None)
    embedding_service.caching_service.cache_embedding = AsyncMock()
    
    embedding = await embedding_service.create_embedding(text="test", db=mock_db)
    
    # Verify result and API call
    assert embedding == mock_result
    embedding_service.client.embeddings.create.assert_called_once()
    embedding_service.caching_service.get_cached_embedding.assert_called_once_with(mock_db, "test")
    embedding_service.caching_service.cache_embedding.assert_called_once_with(mock_db, "test", mock_result)


@pytest.mark.asyncio
async def test_create_embedding_with_cache_hit():
    """Test creating single embedding with database and cache hit."""
    mock_cached_result = [0.2] * 1536
    mock_db = MagicMock()

    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock()
    
    # Mock cache hit
    embedding_service.caching_service.get_cached_embedding = AsyncMock(return_value=mock_cached_result)
    
    embedding = await embedding_service.create_embedding(text="test", db=mock_db)
    
    # Verify result and that API wasn't called
    assert embedding == mock_cached_result
    embedding_service.client.embeddings.create.assert_not_called()
    embedding_service.caching_service.get_cached_embedding.assert_called_once_with(mock_db, "test")


@pytest.mark.asyncio
async def test_batch_create_embedding_no_db():
    """Test creating batch embeddings without database (no caching)."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536]
    
    # Create a response with multiple data items
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=mock_embeddings[0]),
        MagicMock(embedding=mock_embeddings[1])
    ]
    
    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
    
    result = await embedding_service.batch_create_embedding(["text1", "text2"], None)
    
    assert len(result) == 2
    assert result[0] == mock_embeddings[0]
    assert result[1] == mock_embeddings[1]
    embedding_service.client.embeddings.create.assert_called_once()


@pytest.mark.asyncio
async def test_batch_create_embedding_mixed_cache():
    """Test batch embedding with mixed cache hits and misses."""
    mock_db = MagicMock()
    cached_embedding = [0.3] * 1536
    new_embedding = [0.4] * 1536
    
    # Setup response for uncached item
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=new_embedding)]
    
    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
    
    # Setup cache behavior - hit for text1, miss for text2
    async def mock_get_cached(db, text):
        if text == "text1":
            return cached_embedding
        return None
        
    embedding_service.caching_service.get_cached_embedding = AsyncMock(side_effect=mock_get_cached)
    embedding_service.caching_service.cache_embedding = AsyncMock()
    
    result = await embedding_service.batch_create_embedding(["text1", "text2"], db=mock_db)
    
    # Verify results
    assert len(result) == 2
    assert result[0] == cached_embedding  # From cache
    assert result[1] == new_embedding     # From API
    
    # Verify API was called only for uncached text
    embedding_service.client.embeddings.create.assert_called_once_with(
        model=embedding_service.model,
        input=["text2"]
    )
    
    # Verify caching calls
    assert embedding_service.caching_service.get_cached_embedding.call_count == 2
    embedding_service.caching_service.cache_embedding.assert_called_once_with(mock_db, "text2", new_embedding)


@pytest.mark.asyncio
async def test_batch_create_embedding_all_cached():
    """Test batch embedding where all items are cached."""
    mock_db = MagicMock()
    cached_embeddings = [[0.5] * 1536, [0.6] * 1536]
    
    embedding_service = EmbeddingService()
    embedding_service.client.embeddings.create = MagicMock()
    
    # Setup cache hits for all items
    async def mock_get_cached(db, text):
        if text == "text1":
            return cached_embeddings[0]
        return cached_embeddings[1]
        
    embedding_service.caching_service.get_cached_embedding = AsyncMock(side_effect=mock_get_cached)
    
    result = await embedding_service.batch_create_embedding(["text1", "text2"], db=mock_db)
    
    # Verify results
    assert len(result) == 2
    assert result[0] == cached_embeddings[0]
    assert result[1] == cached_embeddings[1]
    
    # API should not be called at all
    embedding_service.client.embeddings.create.assert_not_called()
    
    # Verify cache check calls
    assert embedding_service.caching_service.get_cached_embedding.call_count == 2


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in embedding service."""
    mock_db = MagicMock()
    embedding_service = EmbeddingService()
    
    # Make cache service raise an exception
    embedding_service.caching_service.get_cached_embedding = AsyncMock(side_effect=Exception("Cache error"))
    
    with pytest.raises(Exception):
        await embedding_service.create_embedding("test", mock_db)