from fastapi import FastAPI
from app.api.routes.transfer import create_transfer_router


def create_application() -> FastAPI:
    app = FastAPI()
    transfer_router = create_transfer_router()
    app.include_router(transfer_router)
    return app

app = create_application()
