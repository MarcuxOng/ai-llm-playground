import json
import logging
import uuid

from datetime import datetime
from fastapi import HTTPException
from functools import lru_cache
from pydantic import BaseModel, model_validator, ConfigDict
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from typing import AsyncGenerator, Optional, List

from app.agents import AgentConfig, PRESETS, run_once, build_agent
from app.database.models import Agents, Thread, ThreadMessage
from app.memory.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    tools: List[str]
    model: str
    provider: str


class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    system_prompt: str
    tools: List[str]
    model: str
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    preset: Optional[str] = None       # hardcoded preset name
    agent_id: Optional[str] = None   # DB-backed config id — takes priority
    prompt: str
    thread_id: Optional[str] = None

    @model_validator(mode="after")
    def check_source(self):
        if bool(self.preset) == bool(self.agent_id):
            raise ValueError("Exactly one of 'preset' or 'agent_id' is required.")
        if self.preset and (not self.model or not self.provider):
            raise ValueError("'model' and 'provider' are required when using a 'preset'.")
        return self


class AgentRunResponse(BaseModel):
    answer: str
    preset: Optional[str] = None
    model: str
    provider: str
    thread_id: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    tools: Optional[List[str]] = None
    model: Optional[str] = None
    provider: Optional[str] = None


@lru_cache(maxsize=32)
def _get_cached_agent(
    preset: str, 
    model: str, 
    provider: str, 
    checkpointer_id: int
):
    """
    Cached agent factory to avoid rebuilding the agent on every request.
    Includes checkpointer_id in the cache key to ensure the checkpointer is correctly handled,
    even though get_checkpointer() is also cached.
    """
    checkpointer = get_checkpointer()
    agent_factory = PRESETS[preset]
    return agent_factory(model=model, provider=provider, checkpointer=checkpointer)


async def run_agent_service(
    request: AgentRunRequest, 
    db: Session
) -> AgentRunResponse:
    """
    Unified service for running agents with different providers.
    """
    # Determine agent config
    if request.agent_id:
        agent_config_model = db.query(Agents).filter(
            Agents.id == request.agent_id,
            Agents.is_active.is_(True),
        ).first()
        if not agent_config_model:
            raise HTTPException(status_code=404, detail=f"Agent config {request.agent_id} not found")
        
        system_prompt = agent_config_model.system_prompt
        tools = agent_config_model.tools
        model = agent_config_model.model
        provider = agent_config_model.provider
        preset_name = f"custom:{agent_config_model.name}"
    else:
        if request.preset not in PRESETS:
            raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
        
        model = request.model
        provider = request.provider
        preset_name = request.preset

    # Handle threading
    if request.thread_id:
        thread = db.query(Thread).filter(Thread.id == request.thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread {request.thread_id} not found")
        if (
            thread.preset != preset_name
            or thread.model != model
            or thread.provider != provider
        ):
            raise HTTPException(status_code=400, detail="Thread belongs to a different agent configuration.")
    else:
        thread = Thread(
            id=str(uuid.uuid4()),
            preset=preset_name,
            model=model,
            provider=provider
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)

    try:
        logger.info(f"Running agent with preset: {preset_name}, model: {model}, provider: {provider}, thread: {thread.id}")
        checkpointer = get_checkpointer()

        # Build or get cached agent
        if request.agent_id:
            # Rebuild for now as requested
            agent = await run_in_threadpool(
                build_agent,
                tools=tools,
                system_prompt=system_prompt,
                model=model,
                provider=provider,
                checkpointer=checkpointer
            )
        else:
            agent = await run_in_threadpool(
                _get_cached_agent, 
                request.preset,
                model, 
                provider,
                id(checkpointer)
            )
        
        # Run the agent
        config = AgentConfig(
            name=f"{preset_name.capitalize()} Agent", 
            model=model, 
            provider=provider,
            verbose=False,
        )
        
        lg_config = {"configurable": {"thread_id": thread.id}}
        answer = await run_in_threadpool(
            run_once, 
            agent, 
            request.prompt, 
            config=config,
            lg_config=lg_config
        )
        
        # Save messages
        human_msg = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            role="human",
            content=request.prompt
        )
        db.add(human_msg)
        ai_msg = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            role="ai",
            content=answer
        )
        db.add(ai_msg)
        db.commit()
        
        return AgentRunResponse(
            answer=answer,
            preset=preset_name,
            model=model,
            provider=provider,
            thread_id=thread.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error running agent with {provider}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed for {provider}.") from e


async def run_agent_stream_service(
    request: AgentRunRequest, 
    db: Session
) -> AsyncGenerator[str, None]:
    """
    Unified service for running agents with streaming responses.
    """
    # Determine agent config
    if request.agent_id:
        agent_config_model = db.query(Agents).filter(Agents.id == request.agent_id).first()
        if not agent_config_model:
            raise HTTPException(status_code=404, detail=f"Agent config {request.agent_id} not found")
        
        system_prompt = agent_config_model.system_prompt
        tools = agent_config_model.tools
        model = agent_config_model.model
        provider = agent_config_model.provider
        preset_name = f"custom:{agent_config_model.name}"
    else:
        if request.preset not in PRESETS:
            raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
        
        model = request.model
        provider = request.provider
        preset_name = request.preset

    # Handle threading
    if request.thread_id:
        thread = db.query(Thread).filter(Thread.id == request.thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread {request.thread_id} not found")
    else:
        thread = Thread(
            id=str(uuid.uuid4()),
            preset=preset_name,
            model=model,
            provider=provider
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)

    # Save Human message
    human_msg = ThreadMessage(
        id=str(uuid.uuid4()),
        thread_id=thread.id,
        role="human",
        content=request.prompt
    )
    db.add(human_msg)
    db.commit()

    try:
        logger.info(f"Streaming agent with preset: {preset_name}, model: {model}, provider: {provider}, thread: {thread.id}")
        checkpointer = get_checkpointer()

        # Build or get cached agent
        if request.agent_id:
            agent = await run_in_threadpool(
                build_agent,
                tools=tools,
                system_prompt=system_prompt,
                model=model,
                provider=provider,
                checkpointer=checkpointer
            )
        else:
            agent = await run_in_threadpool(
                _get_cached_agent, 
                request.preset,
                model, 
                provider,
                id(checkpointer)
            )
        
        lg_config = {"configurable": {"thread_id": thread.id}}
        full_answer = ""
        
        async for event in agent.astream_events(
            {"messages": [("human", request.prompt)]},
            config=lg_config,
            version="v2"
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    if isinstance(chunk, str):
                        full_answer += chunk
                    elif isinstance(chunk, list):
                        for part in chunk:
                            if isinstance(part, dict) and part.get("type") == "text":
                                full_answer += part.get("text", "")
                            elif isinstance(part, str):
                                full_answer += part          
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name'], 'input': event['data'].get('input')}, default=str)}\n\n"
            elif kind == "on_tool_end":
                yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name'], 'output': event['data'].get('output')}, default=str)}\n\n"
        
        # Save AI message
        ai_msg = ThreadMessage(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            role="ai",
            content=full_answer
        )
        db.add(ai_msg)
        db.commit()

        yield f"data: {json.dumps({'type': 'done', 'thread_id': thread.id})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:  
        logger.exception(f"Error in streaming agent {provider}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Stream failed'})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'thread_id': thread.id})}\n\n"
        yield "data: [DONE]\n\n"