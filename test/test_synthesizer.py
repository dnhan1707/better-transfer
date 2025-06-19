import sys
import os
import asyncio

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import get_vector_db
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.schemas.transferPlanRequest import TransferPlanRequest

async def main():
    """Test vector search functionality"""
    db = get_vector_db()
    synthesizer = Synthesizer()
    try:
        # Sample query
        query = "What courses do I need to take in 4 terms at Pasadena City College to transfer to University of California, Los Angeles as a Computer Science major?"
        print(f"Searching for: '{query}'")
        transferRequest = TransferPlanRequest(college_id=1, university_id=1, major_id=1)
        # Perform vector search
        vector_res = await VectorStore.vector_search(db, query, transferRequest)
        result = await synthesizer.generate_response(question=query, vector_res=vector_res)

        # Display results
        print("\nSearch Results:")
        print(result)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())