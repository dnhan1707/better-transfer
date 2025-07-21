from fastapi import APIRouter, HTTPException, Depends
from app.services.transfer_service import TransferPlanService
from app.schemas.transferPlanRequest import FullRequest, ReOrderRequestModel, InputRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from bson import ObjectId


def create_transfer_router() -> APIRouter:
    transfer_plan_service = TransferPlanService()
    router = APIRouter(
        prefix="/transfer-plan",
        tags=["Transfer Plan"]
    )
    custom_encoders = {ObjectId: str}

        
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


    @router.post("/test/agreements")
    async def agreements_endpoint(
        request: InputRequest,
    ):
        docs = await transfer_plan_service.get_agreements(request)
        # Use the custom encoder when serialising
        return JSONResponse(
            content=jsonable_encoder(docs, custom_encoder=custom_encoders)
        )


    @router.post("/test/classlist")
    async def classlist_endpoint(
        request: InputRequest,
    ):
        docs = await transfer_plan_service.get_classlist(request)
        return JSONResponse(
            content=jsonable_encoder(docs, custom_encoder=custom_encoders)
        )


    @router.post("/test/v3/transferplan")
    async def transferplan_endpoint_v3(
        request: InputRequest,
    ):
        docs = await transfer_plan_service.get_transferplan(request)
        return JSONResponse(
            content=jsonable_encoder(docs, custom_encoder=custom_encoders)
        )

    return router

