import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.utils.auth import verify_api_key
from app.agents import PRESETS
from app.services.agents import (
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
    run_agent_stream_service
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


@router.post("/run/stream")
async def run_agent_stream(request: AgentRunRequest):
    """
    Endpoint for running agents with streaming responses.
    """
    if request.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    logger.info(f"Starting agent stream with provider: {request.provider}, model: {request.model}")
    response = StreamingResponse(
        run_agent_stream_service(request), 
        media_type="text/event-stream"
    )
    return response