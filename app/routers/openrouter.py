import asyncio
import logging
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.services.openrouter import (
    list_openrouter_models,
    openrouter_service,
    tools_service
)
from app.utils.auth import verify_api_key
from app.utils.response import APIResponse
from app.utils.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/openrouter", 
    tags=["OpenRouter"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models", response_model=APIResponse)
async def get_openrouter_model():
    logger.info("Fetching available OpenRouter models")
    models = list_openrouter_models()
    return APIResponse(data=models)


@router.post("/", response_model=APIResponse)
@limiter.limit("30/minute")
async def openrouter(
    request: Request, 
    body: ProviderInput
):
    logger.info(f"Calling OpenRouter API with model: {body.model}, prompt: {body.prompt}")
    response = await asyncio.to_thread(
        openrouter_service, 
        model=body.model, 
        prompt=body.prompt
    )

    return APIResponse(data=response)


@router.post("/tools", response_model=APIResponse)
@limiter.limit("15/minute")
async def tools(
    request: Request, 
    body: ProviderInput
):
    """
    OpenRouter with tool calling support.
    """
    logger.info(f"Calling OpenRouter tools with model: {body.model}, prompt: {body.prompt}")
    response = await asyncio.to_thread(
        tools_service,
        model=body.model,
        prompt=body.prompt
    )
    return APIResponse(data=response)