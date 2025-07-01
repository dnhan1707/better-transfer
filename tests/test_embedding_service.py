import pytest
from unittest.mock import MagicMock
from RAG.services.embedding_services import EmbeddingService

class DummyEmbeddingResponse:
    def __init__(self, embeddings):
        self.data = [MagicMock(embedding=e) for e in embeddings]

@pytest.mark.asyncio
async def test_create_embedding(monkeypatch):
    service = EmbeddingService()
    response = DummyEmbeddingResponse([[0.1, 0.2]])
    service.client.embeddings.create = MagicMock(return_value=response)

    result = await service.create_embedding("hello")
    assert result == [0.1, 0.2]

@pytest.mark.asyncio
async def test_batch_create_embedding(monkeypatch):
    service = EmbeddingService()
    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    response = DummyEmbeddingResponse(embeddings)
    service.client.embeddings.create = MagicMock(return_value=response)

    result = await service.batch_create_embedding(["a", "b"])
    assert result == embeddings
