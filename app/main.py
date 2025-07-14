from fastapi import FastAPI
from app.api.routes.transfer import create_transfer_router
from fastapi.middleware.cors import CORSMiddleware


def create_application() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    transfer_router = create_transfer_router()
    app.include_router(transfer_router)
    return app

app = create_application()
