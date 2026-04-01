"""
An analyst-focused ReAct agent.
"""

from app.agents.base import build_agent

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
    "web_search",
]

def build_analyst_agent(
    model: str, 
    provider: str, 
    checkpointer=None,
):
    """
    Build and return an analyst ReAct agent.

    Args:
        model: Model name.
        provider: Provider name.
        checkpointer: Optional LangGraph checkpointer.

    Returns:
        A compiled LangGraph agent.
    """
    try:
        res = build_agent(
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            provider=provider,
            checkpointer=checkpointer,
        )
        return res
    except Exception:
        raise