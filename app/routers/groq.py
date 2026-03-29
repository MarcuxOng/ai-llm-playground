import logging
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.groq import (
    get_groq_models, 
    groq_service,
    tools_service
)
from app.utils.response import APIResponse
from app.utils.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/groq", 
    tags=["Groq"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models", response_model=APIResponse)
async def get_groq_model():
    logger.info("Fetching available Groq models")
    models = get_groq_models()
    return APIResponse(data=models)


@router.post("/", response_model=APIResponse)
@limiter.limit("30/minute")
async def groq(
    request: Request, 
    body: ProviderInput
):
    logger.info(f"Calling Groq API with model: {body.model}")
    response = groq_service(
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
    Groq with tool calling support.
    """
    logger.info(f"Calling Groq tools with model: {body.model}")
    response = tools_service(
        model=body.model,
        prompt=body.prompt
    )
    return APIResponse(data=response)