# Better Transfer

Better Transfer is a research project exploring how Retrieval Augmented Generation (RAG) can help community college students plan their academic path when transferring to a four‑year university.

The backend is built with **FastAPI** and stores transfer knowledge in a dedicated pgvector database. OpenAI embeddings and GPT models are used to synthesize a customized transfer plan for each request.

## Features

- Articulation agreements and prerequisite tracking in PostgreSQL
- Vector storage with the pgvector extension and HNSW index
- Async API endpoints to generate transfer plans with or without RAG
- Helper scripts to seed data and populate embeddings
- Docker compose configuration for the vector database

## Getting Started

1. Install Python dependencies:
   ```bash
   pip install -r requirement.txt
   ```
2. Create a `.env` file with at least these values:
   ```
   DATABASE_URL=<application database URL>
   RAG_DATABASE_URL=<vector database URL>
   OPENAI_API_KEY=<your OpenAI key>
   ```
3. Launch PostgreSQL with pgvector:
   ```bash
   docker-compose up -d
   ```
4. Initialize the vector store and insert embeddings:
   ```bash
   python scripts/create_vector_table.py
   python scripts/add_embedding.py
   ```

## Running the API

Start the development server with Uvicorn:
```bash
uvicorn app.main:app --reload
```

The following endpoints are available:
- `POST /transfer-plan` – rule‑based planner
- `POST /transfer-plan/rag` – RAG enhanced planner

## Tests

Run all unit and integration tests with:
```bash
pytest
```

## Project Layout

- `app/` – FastAPI application and database models
- `RAG/` – vector store, embedding service, and GPT synthesizer
- `scripts/` – utilities for seeding and vector generation
- `docker-compose.yml` – container for the pgvector database

## License

This project is released under the MIT License.
