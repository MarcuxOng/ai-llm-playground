import asyncio
import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agents import (
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
)
from app.services.openrouter import (
    list_openrouter_models,
    openrouter_service,
    tools_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/openrouter", tags=["OpenRouter"])


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


@router.post("/agents", response_model=AgentRunResponse)
async def agents(request: AgentRunRequest):
    """
    OpenRouter with agent support.
    """
    logger.info(f"Calling OpenRouter agents with model: {request.model}, prompt: {request.prompt}")
    response = await run_agent_service(
        request, 
        provider="openrouter"
    )
    return response