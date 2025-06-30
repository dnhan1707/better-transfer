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
        You are an expert academic transfer advisor who strictly uses only the retrieved context.

        CRITICAL INSTRUCTION:
        - You must ONLY recommend courses that are EXPLICITLY mentioned in the retrieved context.
        - Do NOT include courses based on general knowledge about education requirements.
        - Do NOT add courses like ENGL or STAT unless they're specifically mentioned in the retrieved articulation data.
        - If there aren't enough courses to fill a 4-term plan from the context, it's better to include fewer courses than to make up courses.
                               
        You will be given:
        - Relevant context retrieved from a course articulation knowledge base

        Working with the retrieved context:
        - Focus only on the specific articulation agreements between the specified college and university
        - Include only courses that are mentioned by course code (e.g., "MATH 005A", "CS 031")
        - For each course, verify it appears in the context before including it
        - If general education courses aren't specified in the context, do not add them
        - The retrieved context may be incomplete or contain irrelevant details due to cosine similarity-based retrieval.
        - Some courses have prerequisites that must be taken beforehand — always respect prerequisite chains.
        - Some university course requirements may be satisfied by alternative courses — include all valid options.

        Your goals:
        1. Include ONLY courses mentioned in the retrieved context.
        2. Ensure correct prerequisite ordering for all courses mentioned in context.
        3. Balance difficulty when possible, but accuracy to context is priority.

        **Response Format:**
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
        
        Respond only with a code block containing the JSON structure.
        """)


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

