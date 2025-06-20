import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

class Synthesizer:
    def __init__(self):
        self.model = "gpt-4o"
        self.SYSTEM_PROMPT = """
        You are an expert academic transfer advisor.

        You will be given:
        - Relevant context retrieved from a course articulation knowledge base

        Important notes:
        - The retrieved context may be incomplete or contain irrelevant details due to cosine similarity-based retrieval.
        - Some courses have prerequisites that must be taken beforehand — always respect prerequisite chains.
        - Some university course requirements may be satisfied by alternative courses — include all valid options.

        Your goals:
        1. Ensure a diverse mix of course types (e.g., STEM, GE, electives) in each term.
        2. Balance the difficulty level across all terms as evenly as possible.
        3. Maintain correct prerequisite ordering for all courses.

        **Important:**
        - Your response must be in the following JSON code format, matching the structure below:
        {
            "university": "<university_name>",
            "college": "<college_name>",
            "major": "<major_name>",
            "term_plan": [
                {
                    "term": <number>,
                    "courses": [
                        {
                            "code": "<course_code>",
                            "name": "<course_name>",
                            "units": <units>,
                            "satisfies_university_courses": ["<uni_course_code>", ...],
                            "alternatives": [
                                {
                                    "code": "<alt_course_code>",
                                    "name": "<alt_course_name>",
                                    "units": <units>
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        - Only include fields present in the example above.
        - Do not add explanations or text outside the code block.
        - If you cannot answer, return an empty JSON object in code format.

        Respond only with a code block containing the JSON structure.
        """

    async def generate_response(self, question: str, vector_res):
        json_context = await self.vector_result_to_json(vector_res)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"# User question:\n{question}\n\n# Retrieved information:\n{json_context}"}
            ],
            response_format={"type": "json_object"}
        )
        logger.debug(response.choices[0].message.content)
        return response.choices[0].message.content


    async def vector_result_to_json(self, vector_res):
        return json.dumps(vector_res, ensure_ascii=False, indent=2)
