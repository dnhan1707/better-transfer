# Better Transfer

Better Transfer is a research project exploring how Retrieval Augmented Generation (RAG) can help community college students plan their academic path when transferring to a four‑year university.

The backend is built with **FastAPI** and stores transfer knowledge in **MongoDB**.  
OpenAI embeddings and GPT models are used to synthesize plans, with caching layers in both MongoDB and Redis.

## Features

- Course and articulation data stored in MongoDB
- Vector search using MongoDB's native vector index
- Redis and MongoDB caching to speed up responses
- Async FastAPI endpoints for transfer plans and plan reordering
- Helper scripts to seed MongoDB collections
- Docker compose configuration for local development

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
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set these values:
   ```
   OPENAI_API_KEY=<your-openai-key>
   MONGO_DB_PCC_CLUSTER_CONNECTION_URL=<mongo-connection>
   MONGO_DB_USERNAME=<username>
   MONGO_DB_PASS=<password>
   REDIS_HOST=<redis-host>
   REDIS_PORT=<redis-port>
   REDIS_USERNAME=<redis-user>
   REDIS_PASSWORD=<redis-pass>
   ```
3. Start the development services:
   ```bash
   docker-compose up -d
   ```
4. Seed MongoDB collections with sample data:
   ```bash
   python scripts/seed_scripts/seed_all.py
   ```

## Running the API

Start the development server with Uvicorn:
```bash
uvicorn app.main:app --reload
```

The following endpoints are available:
- `POST /transfer-plan/v2/rag` – generate a transfer plan with RAG
- `POST /transfer-plan/v2/reorder` – reorder a plan after marking courses as taken
- `GET  /transfer-plan/v1/majorlist/{university_id}/{college_id}` – list majors
- `GET  /transfer-plan/v1/universities` – list universities
- `GET  /transfer-plan/v1/colleges` – list colleges

## Tests

Run all unit and integration tests with:
```bash
pytest
```

## Project Layout

- `app/` – FastAPI application and database models
- `RAG/` – vector store, embedding service, and GPT synthesizer
- `scripts/` – utilities for seeding and vector generation
- `docker-compose.yml` – local stack with FastAPI, MongoDB and Redis

## Prompt Customization

The system prompt for the RAG synthesizer instructs the model to produce **one consolidated transfer plan** that covers all requested universities and majors while minimizing duplicate courses. The guidance to rely solely on retrieved context and to respond using the JSON structure remains unchanged.


## License

This project is released under the MIT License.
