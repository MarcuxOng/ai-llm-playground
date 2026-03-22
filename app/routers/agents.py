import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.agents import build_coder_agent, build_research_agent, run_once, AgentConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["Agents"])


class AgentRunRequest(BaseModel):
    preset: str  # "coder" or "research"
    question: str
    model: str
    provider: str  # "gemini", "groq", "mistral", "openrouter"
    verbose: bool = False


class AgentRunResponse(BaseModel):
    answer: str
    preset: str
    model: str
    provider: str

PRESETS = {
    "coder": build_coder_agent,
    "research": build_research_agent,
}


@router.get("/presets")
async def get_presets():
    """List available agent presets."""
    return {"presets": list(PRESETS.keys())}


@router.post("/", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest):
    """
    Run a specific agent preset with a question.
    """
    if request.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset. Available: {list(PRESETS.keys())}")
    
    try:
        logger.info(f"Running agent with preset: {request.preset}, model: {request.model}, provider: {request.provider}")
        # Build the agent based on preset and provider
        agent_factory = PRESETS[request.preset]
        agent = await run_in_threadpool(
            agent_factory, 
            model=request.model, 
            provider=request.provider
        )
        
        # Run the agent
        config = AgentConfig(
            name=f"{request.preset.capitalize()} Agent", 
            model=request.model, 
            provider=request.provider,
            verbose=request.verbose
        )
        answer = await run_in_threadpool(
            run_once, 
            agent, 
            request.question, 
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
        logger.exception("Error running agent")
        raise HTTPException(status_code=500, detail="Agent execution failed.") from e