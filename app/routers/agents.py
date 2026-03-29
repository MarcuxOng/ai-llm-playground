import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agents import PRESETS
from app.services.agents import (
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
    run_agent_stream_service
)
from app.utils.auth import verify_api_key
from app.utils.response import APIResponse
from app.utils.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/agents", 
    tags=["Agents"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=APIResponse)
async def get_presets():
    """List available agent presets."""
    return APIResponse(data={"presets": list(PRESETS.keys())})


@router.post("/run", response_model=APIResponse[AgentRunResponse])
@limiter.limit("20/minute")
async def run_agent(
    request: Request, 
    body: AgentRunRequest
):
    """
    Unified endpoint for running agents with any supported provider.
    """
    logger.info(f"Calling agents API with provider: {body.provider}, model: {body.model}")
    response = await run_agent_service(body)
    return APIResponse(data=response)


@router.post("/run/stream")
@limiter.limit("20/minute")
async def run_agent_stream(
    request: Request, 
    body: AgentRunRequest
):
    """
    Endpoint for running agents with streaming responses.
    """
    if body.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    logger.info(f"Starting agent stream with provider: {body.provider}, model: {body.model}")
    response = StreamingResponse(
        run_agent_stream_service(body), 
        media_type="text/event-stream"
    )
    return response