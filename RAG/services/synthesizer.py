import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from app.utils.logging_config import get_logger
from RAG.config.settings import get_settings

logger = get_logger(__name__)

load_dotenv()

class Synthesizer:
    def __init__(self):
        settings = get_settings()
        self.model = settings.openai.default_model
        self.client = OpenAI(api_key=settings.openai.api_key)
        self.SYSTEM_PROMPT = settings.synthesizer.system_prompt

    async def generate_response(self, question: str, vector_res):
        json_context = await self.vector_result_to_json(vector_res)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"# User question:\n{question}\n\n# Retrieved information:\n{json_context}"}
            ],
            response_format={"type": "json_object"}
        )
        # Parse the JSON string into a Python dictionary before returning
        json_response = json.loads(response.choices[0].message.content)
        logger.debug("Parsed response: %s", json_response)
        return json_response


    async def vector_result_to_json(self, vector_res):
        return json.dumps(vector_res, ensure_ascii=False, indent=2)
