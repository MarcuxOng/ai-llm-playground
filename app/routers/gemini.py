import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agents import (
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
)
from app.services.gemini import (
    gemini_service, 
    list_gemini_models, 
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gemini", tags=["Gemini"])


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


@router.post("/agents", response_model=AgentRunResponse)
async def agents(request: AgentRunRequest):
    """
    Gemini with agent support.
    """
    logger.info(f"Calling Gemini agents with model: {request.model}, prompt: {request.prompt}")
    response = await run_agent_service(
        request, 
        provider="gemini"
    )
    return response