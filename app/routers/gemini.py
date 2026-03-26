import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.gemini import (
    gemini_service, 
    list_gemini_models, 
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/gemini", 
    tags=["Gemini"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_gemini_model():
    logger.info("Fetching available Gemini models")
    return list_gemini_models()


@router.post("/")
async def gemini(request: ProviderInput):
    logger.info(f"Calling Gemini API with model: {request.model}, prompt: {request.prompt}")
    response = gemini_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    Gemini with tool calling support.
    """
    logger.info(f"Calling Gemini tools with model: {request.model}, prompt: {request.prompt}")
    response = tools_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response