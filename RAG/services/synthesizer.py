import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

class Synthesizer:
    def __init__(self):
        self.model = "gpt-4o"
        self.SYSTEM_PROMPT = """
        You are an expert academic transfer advisor.
        You will receive relevant context retrieved from a knowledge database and a proposed transfer plan.
        Your job is to analyze and answer questions about the transfer plan.
        The context is retrieved based on cosine similarity, so some information might be missing or irrelevant.

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
        # print(response.choices[0].message.content)
        return response.choices[0].message.content


    async def vector_result_to_json(self, vector_res):
        return json.dumps(vector_res, ensure_ascii=False, indent=2)
