import asyncio
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.openrouter import (
    list_openrouter_models,
    openrouter_service,
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/openrouter", 
    tags=["OpenRouter"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_openrouter_model():
    logger.info("Fetching available OpenRouter models")
    return list_openrouter_models()


@router.post("/")
async def openrouter(request: ProviderInput):
    logger.info(f"Calling OpenRouter API with model: {request.model}, prompt: {request.prompt}")
    response = await asyncio.to_thread(
        openrouter_service, 
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    OpenRouter with tool calling support.
    """
    logger.info(f"Calling OpenRouter tools with model: {request.model}, prompt: {request.prompt}")
    response = await asyncio.to_thread(
        tools_service,
        model=request.model,
        prompt=request.prompt
    )
    return response