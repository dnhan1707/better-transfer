import pytest
import json
from unittest.mock import MagicMock
from RAG.services.synthesizer import Synthesizer

@pytest.mark.asyncio
async def test_vector_result_to_json():
    """Test conversion of vector results to JSON."""
    vector_result = [{"id": 1, "content": "Test", "similarity": 0.9}]
    
    synthesizer = Synthesizer()
    json_result = await synthesizer.vector_result_to_json(vector_result)
    
    # Ensure it's valid JSON
    parsed = json.loads(json_result)
    assert len(parsed) == 1
    assert parsed[0]["content"] == "Test"

@pytest.mark.asyncio
async def test_generate_response():
    synthesizer = Synthesizer()
    synthesizer.client.chat.completions.create = MagicMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"answer": "ok"}'))]
        )
    )
    result = await synthesizer.generate_response("hi", [])
    assert result == {"answer": "ok"}
