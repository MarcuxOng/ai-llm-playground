import logging
from fastapi import HTTPException
from functools import lru_cache
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.agents import AgentConfig, PRESETS, run_once

logger = logging.getLogger(__name__)


class AgentRunRequest(BaseModel):
    preset: str  # "coder", "research", or "analyst"
    prompt: str
    model: str
    provider: str


class AgentRunResponse(BaseModel):
    answer: str
    preset: str
    model: str
    provider: str


@lru_cache(maxsize=32)
def _get_cached_agent(preset: str, model: str, provider: str):
    """
    Cached agent factory to avoid rebuilding the agent on every request.
    """
    agent_factory = PRESETS[preset]
    return agent_factory(model=model, provider=provider)


async def run_agent_service(request: AgentRunRequest) -> AgentRunResponse:
    """
    Unified service for running agents with different providers.
    """
    if request.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    
    try:
        logger.info(f"Running agent with preset: {request.preset}, model: {request.model}, provider: {request.provider}")
        # Build or get cached agent
        agent = await run_in_threadpool(
            _get_cached_agent, 
            request.preset,
            request.model, 
            request.provider
        )
        
        # Run the agent
        config = AgentConfig(
            name=f"{request.preset.capitalize()} Agent", 
            model=request.model, 
            provider=request.provider,
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
            provider=request.provider
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error running agent with {request.provider}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed for {request.provider}.") from e