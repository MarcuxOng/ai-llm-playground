import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.groq import (
    get_groq_models, 
    groq_service,
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/groq", 
    tags=["Groq"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_groq_model():
    logger.info("Fetching available Groq models")
    return get_groq_models()


@router.post("/")
async def groq(request: ProviderInput):
    logger.info(f"Calling Groq API with model: {request.model}, prompt: {request.prompt}")
    response = groq_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    Groq with tool calling support.
    """
    logger.info(f"Calling Groq tools with model: {request.model}, prompt: {request.prompt}")
    response = tools_service(
        model=request.model,
        prompt=request.prompt
    )
    return response