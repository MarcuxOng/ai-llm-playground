import json
import logging
from fastapi import HTTPException
from functools import lru_cache
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from typing import AsyncGenerator

from app.agents import AgentConfig, PRESETS, run_once

logger = logging.getLogger(__name__)


class AgentRunRequest(BaseModel):
    provider: str
    model: str
    preset: str  # "coder", "research", "analyst", or "knowledge"
    prompt: str


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


async def run_agent_stream_service(request: AgentRunRequest) -> AsyncGenerator[str, None]:
    """
    Unified service for running agents with streaming responses.
    """
    if request.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    
    try:
        # Build or get cached agent
        agent = await run_in_threadpool(
            _get_cached_agent, 
            request.preset,
            request.model, 
            request.provider
        )
        
        async for event in agent.astream_events(
            {"messages": [("human", request.prompt)]},
            version="v2"
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name'], 'input': event['data'].get('input')})}\n\n"
            elif kind == "on_tool_end":
                yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name'], 'output': event['data'].get('output')})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done', 'thread_id': None})}\n\n"
    except Exception as e:
        logger.exception(f"Error in streaming agent {request.provider}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'thread_id': None})}\n\n"