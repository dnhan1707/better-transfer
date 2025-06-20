import sys
import os
import asyncio

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.schemas.transferPlanRequest import TransferPlanRequest
from app.utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

async def main():
    """Test vector search functionality"""
    db = get_vector_db()
    synthesizer = Synthesizer()
    vector_store = VectorStore()
    try:
        # Sample query
        query = """
        Transfer plan for Computer Science major.
        Target university: University of California, Los Angeles (UCLA).
        Starting college: Pasadena City College (PCC).
        Duration: 4 terms.
        Required: All courses and prerequisites needed to transfer successfully, including any acceptable alternative courses that may satisfy the same requirements.
        """
        logger.info(f"Searching for: '{query}'")
        transferRequest = TransferPlanRequest(college_id=1, university_id=1, major_id=1)
        # Perform vector search
        vector_res = await vector_store.vector_search(db, query, transferRequest)
        result = await synthesizer.generate_response(question=query, vector_res=vector_res)

        # Display results
        logger.info("\nSearch Results:")
        logger.info(result)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())