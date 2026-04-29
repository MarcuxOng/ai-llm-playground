"""
A research-focused ReAct agent.
"""

from typing import List
from langchain_core.tools import BaseTool

from app.agents.base import build_agent


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a research assistant with access to the web.

Guidelines:
- Always search for facts rather than relying on memory when recency matters.
- Fetch the actual page when a search snippet is insufficient (use scrape_url).
- When answering, cite where information came from.
- Be thorough but concise — summarise long pages rather than quoting them wholesale.
- If the user asks about current weather or time, use the appropriate tool.
"""

# ── Factory ───────────────────────────────────────────────────────────────────

TOOLS = [
    "scrape_url", 
    "get_weather", 
    "get_datetime_info",
    "get_news",
    "get_wikipedia_summary",
    "get_youtube_transcript",
]


def build_research_agent(
    model: str, 
    checkpointer=None,
    extra_tools: List[BaseTool] = None,
):
    """
    Build and return a research ReAct agent.

    Args:
        model: Model name.
        checkpointer: Optional LangGraph checkpointer.
        extra_tools: Optional additional LangChain tools.

    Returns:
        A compiled LangGraph agent.
    """
    try:
        combined_tools = TOOLS + (extra_tools or [])
        res = build_agent(
            tools=combined_tools,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            checkpointer=checkpointer,
        )
        return res
    except Exception:
        raise
