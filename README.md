# Better Transfer

Better Transfer is a research project exploring how Retrieval Augmented Generation (RAG) can help community college students plan their academic path when transferring to a four‑year university.

The backend is built with **FastAPI** and stores transfer knowledge in a dedicated pgvector database. OpenAI embeddings and GPT models are used to synthesize a customized transfer plan for each request.

## Features

- Articulation agreements and prerequisite tracking in PostgreSQL
- Vector storage with the pgvector extension and HNSW index
- Async API endpoints to generate transfer plans with or without RAG
- Helper scripts to seed data and populate embeddings
- Docker compose configuration for the vector database

## 📦 Sample Response

This example shows how Better Transfer generates a plan that satisfies:
- 🎯 **UCLA – Computer Science**
- 🎯 **UC Berkeley – Data Science**
- 🏫 From: **Pasadena City College**

View the full optimized plan:  
📄 [`examples/multi_university_sample.json`](./examples/multi_university_sample.json)

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
   alembic init alembic
   alembic revision --autogenerate -m "create models"
   python scripts/seed_better_transfer_db.py
   python scripts/seed_embedding_vector_db.py
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

## Prompt Customization

The system prompt for the RAG synthesizer instructs the model to produce **one consolidated transfer plan** that covers all requested universities and majors while minimizing duplicate courses. The guidance to rely solely on retrieved context and to respond using the JSON structure remains unchanged.


## License

This project is released under the MIT License.
