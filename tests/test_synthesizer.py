import pytest
from unittest.mock import MagicMock
from RAG.services.synthesizer import Synthesizer

class DummyChatResponse:
    def __init__(self, content):
        self.choices = [MagicMock(message=MagicMock(content=content))]

@pytest.mark.asyncio
async def test_vector_result_to_json():
    synth = Synthesizer()
    data = [{"id": 1, "content": "hello"}]
    json_result = await synth.vector_result_to_json(data)
    assert "hello" in json_result

@pytest.mark.asyncio
async def test_generate_response(monkeypatch):
    synth = Synthesizer()
    synth.client.chat.completions.create = MagicMock(return_value=DummyChatResponse('{"answer": "ok"}'))
    result = await synth.generate_response("hi", [])
    assert result == {"answer": "ok"}
