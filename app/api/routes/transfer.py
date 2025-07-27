from fastapi import APIRouter, HTTPException
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import FullRequest, ReOrderRequestModel
from app.utils.cache_wrapper import cache_response

def create_transfer_router() -> APIRouter:
    transfer_plan_service = TransferPlanService()
    router = APIRouter(
        prefix="/transfer-plan",
        tags=["Transfer Plan"]
    )

    @router.post("/v2/rag")
    async def rag_transfer_plan_v2(
        request: FullRequest,
    ):
        try:
            return await transfer_plan_service.create_RAG_transfer_plan_v2(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/v2/reorder")
    async def re_order_plan_v2(
        request: ReOrderRequestModel, 
    ):
        try:
            return await transfer_plan_service.re_order_transfer_plan_v2(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/v1/majorlist/{university_id}/{college_id}")
    @cache_response("major_list:{university_id}:{college_id}", expiration=3600)  # 1 hour
    async def major_list(university_id: str, college_id: str):
        try:
            return await transfer_plan_service.get_major_list(university_id, college_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/v1/universities")
    @cache_response("universities_list", expiration=21600)  # 6 hours
    async def get_universities():
        """Get list of all universities"""
        try:
            return await transfer_plan_service.get_universities()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/v1/colleges")
    @cache_response("colleges_list", expiration=21600)  # 6 hours
    async def get_colleges():
        """Get list of all colleges"""
        try:
            return await transfer_plan_service.get_colleges()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router