from fastapi import APIRouter, HTTPException
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import FullRequest, ReOrderRequestModel


def create_transfer_router() -> APIRouter:
    transfer_plan_service = TransferPlanService()
    router = APIRouter(
        prefix="/transfer-plan",
        tags=["Transfer Plan"]
    )
        
    @router.post("/v2/rag")
    async def rag_transfer_plan_v2(
        request:     FullRequest,
    ):
        try:
            return await transfer_plan_service.create_RAG_transfer_plan_v2(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/v2/reorder")
    async def re_order_plan_v2(
        request:     ReOrderRequestModel, 
    ):
        try:
            return await transfer_plan_service.re_order_transfer_plan_v2(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
