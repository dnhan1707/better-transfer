import pytest
from unittest.mock import MagicMock, patch
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.schemas.transferPlanRequest import TransferPlanRequest

@pytest.mark.asyncio
async def test_search_and_synthesize(patch_get_vector_db):
    mock_db = patch_get_vector_db
    first_call = MagicMock()
    first_call.fetchall.return_value = [
        (1, "content1", "college", "uni", "major", "course_des", 0.9)
    ]
    second_call = MagicMock()
    second_call.fetchall.return_value = []
    mock_db.execute.side_effect = [first_call, second_call]

    with patch('RAG.services.embedding_services.EmbeddingService.create_embedding', return_value=[0.1]*1536):
        store = VectorStore()
        results = await store.vector_search("query", TransferPlanRequest(college_id=1, university_id=1, major_id=1))

    synth = Synthesizer()
    synth.client.chat.completions.create = MagicMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"res": 1}'))]
    ))
    response = await synth.generate_response("query", results)

    assert response == {"res": 1}
