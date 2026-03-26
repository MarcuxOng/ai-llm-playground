import logging
from fastapi import APIRouter, Depends

from app.utils.auth import verify_api_key
from app.agents import PRESETS
from app.services.agents import (
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/agents", 
    tags=["Agents"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/")
async def get_presets():
    """List available agent presets."""
    return {"presets": list(PRESETS.keys())}


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest):
    """
    Unified endpoint for running agents with any supported provider.
    """
    logger.info(f"Calling agents API with provider: {request.provider}, model: {request.model}")
    response = await run_agent_service(request)
    return response