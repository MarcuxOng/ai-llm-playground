import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.agents import PRESETS
from app.database.db import get_db
from app.database.models import Agents
from app.services.agents import (
    AgentCreate,
    AgentResponse,
    AgentRunRequest, 
    AgentRunResponse,
    run_agent_service, 
    run_agent_stream_service
)
from app.tools import _REGISTRY
from app.utils.auth import verify_api_key
from app.utils.response import APIResponse
from app.utils.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/agents", 
    tags=["Agents"],
    dependencies=[Depends(verify_api_key)]
)


@router.get("/list", response_model=APIResponse[List[AgentResponse]])
async def list_agents(db: Session = Depends(get_db)):
    configs = db.query(Agents).filter(
        Agents.is_active == True
    ).all()
    return APIResponse(data=[AgentResponse.model_validate(c) for c in configs])


@router.get("/presets", response_model=APIResponse)
async def get_presets():
    """List available agent presets."""
    return APIResponse(data={"presets": list(PRESETS.keys())})


@router.post("/create", response_model=APIResponse[AgentResponse])
async def create_agent(
    body: AgentCreate, 
    db: Session = Depends(get_db)
):
    # Validate requested tools exist in registry
    unknown = [t for t in body.tools if t not in _REGISTRY]
    if unknown:
        raise HTTPException(400, detail=f"Unknown tools: {unknown}, Available: {list(_REGISTRY.keys())}")

    config = Agents(**body.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return APIResponse(data=AgentResponse.model_validate(config))


@router.patch("/{agent_id}", response_model=APIResponse[AgentResponse])
async def update_agent_config(
    agent_id: str, 
    body: AgentCreate,
    db: Session = Depends(get_db)
):
    config = db.query(Agents).filter(
        Agents.id == agent_id
    ).first()
    
    if not config:
        raise HTTPException(404, "Config not found.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return APIResponse(data=AgentResponse.model_validate(config))


@router.delete("/{agent_id}", response_model=APIResponse)
async def delete_agent_config(
    agent_id: str, 
    db: Session = Depends(get_db)
):
    config = db.query(Agents).filter(
        Agents.id == agent_id
    ).first()
    
    if not config:
        raise HTTPException(404, "Config not found.")
    config.is_active = False
    db.commit()
    return APIResponse(data={"message": f"Config {agent_id} deactivated."})


@router.post("/run", response_model=APIResponse[AgentRunResponse])
@limiter.limit("20/minute")
async def run_agent(
    request: Request, 
    body: AgentRunRequest,
    db: Session = Depends(get_db)
):
    """
    Unified endpoint for running agents with any supported provider.
    """
    logger.info(f"Calling agents API with provider: {body.provider}, model: {body.model}")
    response = await run_agent_service(body, db)
    return APIResponse(data=response)


@router.post("/run/stream")
@limiter.limit("20/minute")
async def run_agent_stream(
    request: Request, 
    body: AgentRunRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint for running agents with streaming responses.
    """
    logger.info(f"Starting agent stream with provider: {body.provider}, model: {body.model}")
    response = StreamingResponse(
        run_agent_stream_service(body, db), 
        media_type="text/event-stream"
    )
    return response


@router.get("/tools", response_model=APIResponse)
async def list_available_tools():
    """List all registered tools that can be assigned to an agent config."""
    tools = [
        {
            "name": name,
            "description": entry["schema"]["function"]["description"],
            "parameters": entry["schema"]["function"]["parameters"],
        }
        for name, entry in _REGISTRY.items()
    ]
    return APIResponse(data=tools)