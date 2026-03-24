import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mistral import (
    list_mistral_models, 
    mistral_service,
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mistral", tags=["Mistral"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_mistral_model():
    logger.info("Fetching available Mistral models")
    return list_mistral_models()


@router.post("/")
async def mistral(request: ProviderInput):
    logger.info(f"Calling Mistral API with model: {request.model}, prompt: {request.prompt}")
    response = mistral_service(
        model=request.model,
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    Mistral with tool calling support.
    """
    logger.info(f"Calling Mistral tools with model: {request.model}, prompt: {request.prompt}")
    response = tools_service(
        model=request.model,
        prompt=request.prompt
    )
    return response