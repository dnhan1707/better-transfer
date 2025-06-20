import sys
import os
import asyncio

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from RAG.db.vector_store import VectorStore
from app.schemas.transferPlanRequest import TransferPlanRequest
from app.utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

async def main():
    """Test vector search functionality"""
    db = get_vector_db()
    vector_store = VectorStore()
    try:
        # Sample query
        query = """
        Transfer plan for Computer Science major.
        Target university: University of California, Los Angeles (UCLA).
        Starting college: Pasadena City College (PCC).
        Duration: 4 terms.
        Required: All courses and prerequisites needed to transfer successfully.
        """
        logger.info(f"Searching for: '{query}'")
        transferRequest = TransferPlanRequest(college_id=1, university_id=1, major_id=1)
        # Perform vector search
        results = await vector_store.vector_search(db, query, transferRequest)
        
        # Display results
        logger.info("\nSearch Results:")
        logger.info("-" * 80)
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. Similarity: {result['similarity']:.4f}")
            if result['college_name']:
                logger.info(f"   College: {result['college_name']}")
            if result['university_name']:
                logger.info(f"   University: {result['university_name']}")
            if result['major_name']:
                logger.info(f"   Major: {result['major_name']}")
            logger.info(f"   Type: {result['chunk_type']}")
            logger.info(f"   Content: {result['content']}")
            logger.info("-" * 80)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())