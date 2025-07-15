import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from RAG.services.embedding_services import EmbeddingService

class MockResponse:
    def __init__(self, embedding):
        self.data = [MagicMock(embedding=embedding)]

@pytest.mark.asyncio
async def test_create_embedding_no_cache():
    """Test creating single embedding without caching."""
    mock_result = [0.1] * 1536

    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service:
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=MockResponse(mock_result))
        
        # Call with use_cache=False
        embedding = await embedding_service.create_embedding("test", use_cache=False)
        
        # Verify result and API call
        assert embedding == mock_result
        embedding_service.client.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_embedding_with_cache_miss():
    """Test creating single embedding with cache miss."""
    mock_result = [0.1] * 1536

    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        mock_caching_service.get_cached_embedding.return_value = None
        mock_caching_service.cache_embedding.return_value = None
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=MockResponse(mock_result))
        
        embedding = await embedding_service.create_embedding("test", use_cache=True)
        
        # Verify result and API call
        assert embedding == mock_result
        embedding_service.client.embeddings.create.assert_called_once()
        mock_caching_service.get_cached_embedding.assert_called_once_with("test")
        mock_caching_service.cache_embedding.assert_called_once_with("test", mock_result)

@pytest.mark.asyncio
async def test_create_embedding_with_cache_hit():
    """Test creating single embedding with cache hit."""
    mock_cached_result = [0.2] * 1536

    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        mock_caching_service.get_cached_embedding.return_value = mock_cached_result
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock()
        
        embedding = await embedding_service.create_embedding("test", use_cache=True)
        
        # Verify result and that API wasn't called
        assert embedding == mock_cached_result
        embedding_service.client.embeddings.create.assert_not_called()
        mock_caching_service.get_cached_embedding.assert_called_once_with("test")

@pytest.mark.asyncio
async def test_batch_create_embedding_no_cache():
    """Test creating batch embeddings without caching."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536]
    
    # Create a response with multiple data items
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=mock_embeddings[0]),
        MagicMock(embedding=mock_embeddings[1])
    ]
    
    with patch('RAG.services.embedding_services.CachingService'):
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
        
        result = await embedding_service.batch_create_embedding(["text1", "text2"], use_cache=False)
        
        assert len(result) == 2
        assert result[0] == mock_embeddings[0]
        assert result[1] == mock_embeddings[1]
        embedding_service.client.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_batch_create_embedding_mixed_cache():
    """Test batch embedding with mixed cache hits and misses."""
    cached_embedding = [0.3] * 1536
    new_embedding = [0.4] * 1536
    
    # Setup response for uncached item
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=new_embedding)]
    
    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        
        # Setup cache behavior - hit for text1, miss for text2
        async def mock_get_cached(text):
            if text == "text1":
                return cached_embedding
            return None
            
        mock_caching_service.get_cached_embedding.side_effect = mock_get_cached
        mock_caching_service.cache_embedding.return_value = None
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
        
        result = await embedding_service.batch_create_embedding(["text1", "text2"], use_cache=True)
        
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
        assert mock_caching_service.get_cached_embedding.call_count == 2
        mock_caching_service.cache_embedding.assert_called_once_with("text2", new_embedding)

@pytest.mark.asyncio
async def test_batch_create_embedding_all_cached():
    """Test batch embedding where all items are cached."""
    cached_embeddings = [[0.5] * 1536, [0.6] * 1536]
    
    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        
        # Setup cache hits for all items
        async def mock_get_cached(text):
            if text == "text1":
                return cached_embeddings[0]
            return cached_embeddings[1]
            
        mock_caching_service.get_cached_embedding.side_effect = mock_get_cached
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock()
        
        result = await embedding_service.batch_create_embedding(["text1", "text2"], use_cache=True)
        
        # Verify results
        assert len(result) == 2
        assert result[0] == cached_embeddings[0]
        assert result[1] == cached_embeddings[1]
        
        # API should not be called at all
        embedding_service.client.embeddings.create.assert_not_called()
        
        # Verify cache check calls
        assert mock_caching_service.get_cached_embedding.call_count == 2

@pytest.mark.asyncio
async def test_create_embedding_no_cache_method():
    """Test the no_cache convenience method."""
    mock_result = [0.1] * 1536

    with patch('RAG.services.embedding_services.CachingService'):
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=MockResponse(mock_result))
        
        embedding = await embedding_service.create_embedding_no_cache("test")
        
        assert embedding == mock_result
        embedding_service.client.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_batch_create_embedding_no_cache_method():
    """Test the batch no_cache convenience method."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536]
    
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=mock_embeddings[0]),
        MagicMock(embedding=mock_embeddings[1])
    ]
    
    with patch('RAG.services.embedding_services.CachingService'):
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
        
        result = await embedding_service.batch_create_embedding_no_cache(["text1", "text2"])
        
        assert len(result) == 2
        assert result[0] == mock_embeddings[0]
        assert result[1] == mock_embeddings[1]

@pytest.mark.asyncio
async def test_error_handling_cache_error():
    """Test error handling when caching service fails."""
    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        mock_caching_service.get_cached_embedding.side_effect = Exception("Cache error")
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        
        with pytest.raises(Exception, match="Cache error"):
            await embedding_service.create_embedding("test", use_cache=True)

@pytest.mark.asyncio
async def test_error_handling_openai_api_error():
    """Test error handling when OpenAI API fails."""
    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        mock_caching_service.get_cached_embedding.return_value = None
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(side_effect=Exception("API error"))
        
        with pytest.raises(Exception, match="API error"):
            await embedding_service.create_embedding("test", use_cache=True)

@pytest.mark.asyncio
async def test_generate_embeddings_internal_method():
    """Test the internal _generate_embeddings method."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536]
    
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=mock_embeddings[0]),
        MagicMock(embedding=mock_embeddings[1])
    ]
    
    with patch('RAG.services.embedding_services.CachingService'):
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
        
        result = await embedding_service._generate_embeddings(["text1", "text2"])
        
        assert len(result) == 2
        assert result[0] == mock_embeddings[0]
        assert result[1] == mock_embeddings[1]
        
        embedding_service.client.embeddings.create.assert_called_once_with(
            model=embedding_service.model,
            input=["text1", "text2"]
        )

@pytest.mark.asyncio
async def test_batch_embedding_order_preservation():
    """Test that batch embeddings preserve the order of input texts."""
    # Test with some texts cached and some not, in mixed order
    cached_embeddings = {
        "text1": [0.1] * 1536,
        "text3": [0.3] * 1536
    }
    
    new_embeddings = [[0.2] * 1536, [0.4] * 1536]  # For text2 and text4
    
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=new_embeddings[0]),
        MagicMock(embedding=new_embeddings[1])
    ]
    
    with patch('RAG.services.embedding_services.CachingService') as mock_caching_service_class:
        mock_caching_service = AsyncMock()
        
        async def mock_get_cached(text):
            return cached_embeddings.get(text, None)
            
        mock_caching_service.get_cached_embedding.side_effect = mock_get_cached
        mock_caching_service.cache_embedding.return_value = None
        mock_caching_service_class.return_value = mock_caching_service
        
        embedding_service = EmbeddingService()
        embedding_service.client.embeddings.create = MagicMock(return_value=mock_response)
        
        texts = ["text1", "text2", "text3", "text4"]
        result = await embedding_service.batch_create_embedding(texts, use_cache=True)
        
        # Verify order is preserved
        assert len(result) == 4
        assert result[0] == cached_embeddings["text1"]  # From cache
        assert result[1] == new_embeddings[0]  # From API (text2)
        assert result[2] == cached_embeddings["text3"]  # From cache
        assert result[3] == new_embeddings[1]  # From API (text4)
        
        # Verify API was called only for uncached texts in correct order
        embedding_service.client.embeddings.create.assert_called_once_with(
            model=embedding_service.model,
            input=["text2", "text4"]
        )