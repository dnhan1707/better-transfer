┌────────────────────────────┐
│        External            │ ← UI, DB, API, Email, etc.
└────────────────────────────┘
           ↓
┌────────────────────────────┐
│     Interface Adapters     │ ← e.g. FastAPI routes, request parsing, DB adapters
└────────────────────────────┘
           ↓
┌────────────────────────────┐
│   Application Services     │ ← Business logic, orchestrating use cases
└────────────────────────────┘
           ↓
┌────────────────────────────┐
│      Domain Entities       │ ← Models, core rules, validation
└────────────────────────────┘


### Tools & Stack

| **Layer**           | **Technology**                                                               |
|---------------------|------------------------------------------------------------------------------|
| **API / Interface** | FastAPI, Pydantic                                                            |
| **Service Logic**   | Custom Python modules (business logic)                                       |
| **DB Access**       | SQLAlchemy (ORM) or Tortoise ORM                                             |
| **Database**        | PostgreSQL                                                                   |
| **Testing**         | `pytest`, `httpx` (for endpoint testing)                                     |
| **Dev Environment** | Docker, Poetry or Pipenv, `.env` configurations                              |
| **CI/CD**           | GitHub Actions, Railway / Render / Vercel (for backend deployment)           |
| **Optional**        | Redis (for caching), Celery (for background tasks)                           |
