from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from functools import lru_cache
from app.utils.logging_config import get_logger
logger = get_logger(__name__)

import os

load_dotenv()

class LLMSettings(BaseModel):
    max_tokens: Optional[int] = None
    max_retries: int = Field(default=3)


class OpenAISettings(LLMSettings):
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    default_model: str = Field(default="gpt-4o")
    embedding_model: str =  Field(default="text-embedding-ada-002")

class DatabaseSettings(BaseModel):
    service_url: str = Field(default_factory=lambda: os.getenv("RAG_DATABASE_URL"))

class VectorStoreSettings(BaseModel):
    embedding_dimensions: int = 1536
    table_name: str = "knowledge_chunks"

class SynthesizerSettings(BaseModel):
    system_prompt: str = Field(default="""
        You are an expert academic transfer advisor. Your role is to generate a single, optimized **transfer plan** that satisfies course requirements for **multiple target universities and majors**, using only the retrieved articulation data.

        =====================
        STRICT CONSTRAINTS
        =====================
        - ONLY include courses that are **explicitly present in the retrieved context**.
        - Do NOT infer or add any courses based on general knowledge.
        - Do NOT include common GE courses like ENGL or STAT unless explicitly listed in the retrieved data.
        - The plan must be a **unified plan** that satisfies **ALL target university-major pairs**, whenever possible.
        - You MUST include EVERY SINGLE COURSE mentioned in articulation agreements in an optimized way

        ==========================
        OPTIMIZATION OBJECTIVES
        ==========================
        1. **Maximize Course Overlap** – prioritize courses that satisfy requirements for multiple universities/majors.
        2. **Minimize Total Courses** – avoid redundancy; each course should serve as many purposes as possible.
        3. **Respect Prerequisites** – maintain correct sequencing of courses.
        4. **Balance Course Load** – distribute difficult or high-unit courses evenly across terms.

        =========================
        GUIDELINES FOR CONTEXT USE
        =========================
        - Only recommend courses if they are found in the retrieved context.
        - Highlight "versatile courses" that fulfill requirements for multiple targets.
        - For each course, explicitly state **which university and major requirements it satisfies**.
        - If a course only satisfies a single target, clearly indicate that limitation.

        ==================
        RESPONSE FORMAT
        ==================
        Respond **only** with a JSON code block, using the following structure:

        ```json
        {
        "targets": [
            {"university": "<university1_name>", "major": "<major1_name>"},
            {"university": "<university2_name>", "major": "<major2_name>"}
        ],
        "source_college": "<college_name>",
        "term_plan": [
            {
            "term": <term_number>,
            "courses": [
                {
                "code": "<course_code>",
                "name": "<course_name>",
                "units": <units>,
                "satisfies": [
                    {
                    "university": "<university_name>",
                    "major": "<major_name>",
                    "university_courses": ["<university_course_code>", ...]
                    }
                ],
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
        }""")

class Settings(BaseModel):
    """This include all the settings"""
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    synthesizer: SynthesizerSettings = Field(default_factory=SynthesizerSettings)

@lru_cache
def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise

