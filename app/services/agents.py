import logging
from fastapi import HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.agents import AgentConfig, PRESETS, run_once

logger = logging.getLogger(__name__)


class AgentRunRequest(BaseModel):
    preset: str  # "coder", "research", or "analyst"
    prompt: str
    model: str


class AgentRunResponse(BaseModel):
    answer: str
    preset: str
    model: str
    provider: str


async def run_agent_service(request: AgentRunRequest, provider: str) -> AgentRunResponse:
    """
    Unified service for running agents with different providers.
    """
    if request.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    
    try:
        logger.info(f"Running agent with preset: {request.preset}, model: {request.model}, provider: {provider}")
        # Build the agent based on preset and provider
        agent_factory = PRESETS[request.preset]
        agent = await run_in_threadpool(
            agent_factory, 
            model=request.model, 
            provider=provider
        )
        
        # Run the agent
        config = AgentConfig(
            name=f"{request.preset.capitalize()} Agent", 
            model=request.model, 
            provider=provider,
            verbose=False,
        )
        answer = await run_in_threadpool(
            run_once, 
            agent, 
            request.prompt, 
            config=config
        )
        
        return AgentRunResponse(
            answer=answer,
            preset=request.preset,
            model=request.model,
            provider=provider
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error running agent with {provider}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed for {provider}.") from e