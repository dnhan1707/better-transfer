from fastapi import FastAPI
from app.api.routes.transfer import create_transfer_router
from fastapi.middleware.cors import CORSMiddleware


def create_application() -> FastAPI:
    app = FastAPI(
        title="Better Transfer API",
        description="Transfer planning API with RAG capabilities",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=False,  
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Health check endpoint for Azure
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "Better Transfer API is running"}
    
    transfer_router = create_transfer_router()
    app.include_router(transfer_router)
    return app

app = create_application()