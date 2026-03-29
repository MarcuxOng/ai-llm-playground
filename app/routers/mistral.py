import logging
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.mistral import (
    list_mistral_models, 
    mistral_service,
    tools_service
)
from app.utils.response import APIResponse
from app.utils.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/mistral", 
    tags=["Mistral"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models", response_model=APIResponse)
async def get_mistral_model():
    logger.info("Fetching available Mistral models")
    models = list_mistral_models()
    return APIResponse(data=models)


@router.post("/", response_model=APIResponse)
@limiter.limit("30/minute")
async def mistral(
    request: Request, 
    body: ProviderInput
):
    logger.info(f"Calling Mistral API with model: {body.model}, prompt: {body.prompt}")
    response = mistral_service(
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
    Mistral with tool calling support.
    """
    logger.info(f"Calling Mistral tools with model: {body.model}, prompt: {body.prompt}")
    response = tools_service(
        model=body.model,
        prompt=body.prompt
    )
    return APIResponse(data=response)