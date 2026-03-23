from app.agents.base import build_agent
from app.agents.runner import run_once, AgentConfig
from app.agents.presets.coder import build_coder_agent
from app.agents.presets.research import build_research_agent
from app.agents.presets.analyst import build_analyst_agent

__all__ = [
    "build_agent",
    "run_once",
    "AgentConfig",
    "build_coder_agent",
    "build_research_agent",
    "build_analyst_agent",
]

PRESETS = {
    "coder": build_coder_agent,
    "research": build_research_agent,
    "analyst": build_analyst_agent,
}
