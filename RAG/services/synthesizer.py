from openai import OpenAI
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

    async def generate_response(self, question: str, number_of_terms, vector_res):
        json_context = await self.vector_result_to_json(vector_res)
        system_prompt = f"""
            You are an expert academic transfer advisor.  
            ► The user has requested **EXACTLY {number_of_terms} academic terms**.

            You will receive:
            • **Context** – JSON rows from a course-articulation knowledge base.  
            Each row may include  
            − `id`     unique row ID (optional)  
            − `chunk_type` 'articulation', 'class', 'prerequisite', 'ge', …  
            − `content`  natural-language mapping or detail

            --------------------  CRITICAL RULES  --------------------
            1. MUST-INCLUDE CHECKLIST  
            • Every PCC course mentioned in any row where `chunk_type == "articulation"`
                **must** be scheduled.  
            • If an articulation row lists multiple PCC course codes separated by commas,
                slashes, or the word “and” (e.g. “PHYS 008A/008B/008C”), treat **each code
                as a separate course** that must be placed.

            2. TERM COUNT  
            • Use exactly **{number_of_terms} terms** (no more, no less).  
            • Do **not** create extra terms, summer sessions, or remove courses just
                to lighten a heavy load.

            3. PREREQUISITE HANDLING  
            • Some courses have prerequisites that must be taken beforehand — always respect prerequisite chains.
            • Some university course requirements may be satisfied by alternative courses — include all valid options.
            • If correct ordering is impossible, **still place the course** and add a
                `"note"` field, e.g.  
                `"note": "Concurrent with prerequisite MATH 005A; allowed but not recommended."`

            4. NO HALLUCINATIONS  
            • Use only PCC course codes present in the context.  
            • If you encounter a truly invalid or duplicate mapping that cannot be
                scheduled at all, you may create an `unscheduled_courses` array with a
                brief reason; do **not** add extra terms.

            5. UNIFIED PLAN  
            • Produce one schedule that satisfies **all** university-major targets while
                minimising duplicate PCC courses and balancing units/difficulty across the
                fixed number of terms.
            
            6. NO EXTRA COURSES  
            • Schedule **only** courses that meet at least one of these conditions:  
                – appears in an `articulation` row for any target university/major, **or**  
                – is an explicit prerequisite of a scheduled course.  
            • Do NOT add electives, GEs, or “nice-to-have” courses unless they satisfy
                the rule above.
                
            CRITICAL INSTRUCTION:
            • Do NOT add courses like ENGL or STAT unless they're specifically mentioned in the retrieved articulation data.



            --------------------  OPTIMISATION GOALS  ----------------
            • Distribute difficult courses evenly across terms.  
            • Ensure a mix of STEM, GE, and electives each term when possible.  
            • Minimise total units while satisfying every requirement.  
            • For alternatives containing “placement”, include `{{ "need_placement": true }}`.

            --------------------  OUTPUT SCHEMA  ---------------------
            ```json
            {{
            "targets": [
                {{"university": "<university1>", "major": "<major1>"}},
                {{"university": "<university2>", "major": "<major2>"}}
            ],
            "source_college": "<college_name>",
            "term_plan": [
                {{
                "term": <int>,                 // 1 … {number_of_terms}
                "courses": [
                    {{
                    "code": "<PCC_course_code>",
                    "name": "<PCC_course_name>",
                    "units": <float>,
                    "difficulty": <1-5>,
                    "prerequisites": [ ... ],
                    "satisfies": [
                        {{
                        "university": "<university>",
                        "major": "<major>",
                        "university_courses": ["<univ_course_code>", ...]
                        }}
                    ],
                    "alternatives": [ ... ],
                    "note": <string>
                    }}
                ]
                }}
            ],
            "unscheduled_courses": [           // include only if Rule 4 applies
                {{
                "code": "<PCC_course_code>",
                "reason": "<short explanation>"
                }}
            ]
            }}
            ```"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"# User question:\n{question}\n\n# Retrieved information:\n{json_context}"}
            ],
            response_format={"type": "json_object"}
        )
        # Parse the JSON string into a Python dictionary before returning
        json_response = json.loads(response.choices[0].message.content)
        logger.debug("Parsed response: %s", json_response)
        return json_response


    async def generate_reorder_plan_response(self, question: str, courses_data):
        json_context = await self.vector_result_to_json(courses_data)
        system_prompt = f"""
            You are an expert academic advisor responsible for reorganizing a student's transfer plan 
            after they've marked some courses as already taken.
            
            Your task is to:
            1. Remove courses that are marked as "taken" from the plan
            2. Redistribute remaining courses across the same number of terms
            3. Respect all prerequisite requirements
            4. Balance course difficulty across terms
            5. Ensure a variety of course types in each term
            6. Preserve the overall structure and format of the plan
            
            IMPORTANT CONSTRAINTS:
            - Do NOT add any new courses that weren't in the original plan
            - Maintain the same number of terms as the original plan
            - Keep all required courses from the original plan that haven't been taken
            - If a prerequisite has been taken, courses dependent on it can be moved earlier
            - Output must follow the exact same JSON format as the original plan
            
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"# User question:\n{question}\n\n# Retrieved information:\n{json_context}"}
            ],
            response_format={"type": "json_object"}
        )
        json_response = json.loads(response.choices[0].message.content)
        logger.debug("Parsed response: %s", json_response)
        return json_response

    async def vector_result_to_json(self, vector_res):
        return json.dumps(vector_res, ensure_ascii=False, indent=2)
