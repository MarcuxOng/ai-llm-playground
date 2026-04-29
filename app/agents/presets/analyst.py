"""
An analyst-focused ReAct agent.
"""

from typing import List
from langchain_core.tools import BaseTool

from app.agents.base import build_agent, merge_tools

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a financial analyst with access to the stock market and cryptocurrency data.

Guidelines:
- Always search for facts rather than relying on memory when recency matters.
- Fetch the actual page when a search snippet is insufficient.
- When answering, cite where information came from.
- Be thorough but concise — summarise long pages rather than quoting them wholesale.
"""

# ── Factory ───────────────────────────────────────────────────────────────────
TOOLS = [
    "get_stock_price",
    "get_crypto_price",
]

def build_analyst_agent(
    model: str, 
    checkpointer=None,
    extra_tools: List[BaseTool] = None,
):
    """
    Build and return an analyst ReAct agent.

    Args:
        model: Model name.
        checkpointer: Optional LangGraph checkpointer.
        extra_tools: Optional additional LangChain tools.

    Returns:
        A compiled LangGraph agent.
    """
    try:
        combined_tools = merge_tools(TOOLS, extra_tools)
        res = build_agent(
            tools=combined_tools,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            checkpointer=checkpointer,
        )
        return res
    except Exception:
        raise