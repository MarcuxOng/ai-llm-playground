"""
A coding-focused ReAct agent.
"""

from app.agents.base import build_agent


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a senior software engineer and coding assistant.

Guidelines:
- Write clean code with type hints.
- Use comments to explain complex logic.
- Follow best practices for code structure and design.
- Write maintainable and scalable code.
- Explain your reasoning briefly before presenting the final code.
"""

# ── Factory ───────────────────────────────────────────────────────────────────

TOOLS = [
    "calculate", 
    "read_file", 
    "write_file",
    "test_regex",
    "count_tokens",
]


def build_coder_agent(model: str, provider: str):
    """
    Build and return a coding ReAct agent.

    Args:
        model: Model name.
        provider: Provider name.

    Returns:
        A compiled LangGraph agent.
    """
    try:
        res = build_agent(
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            provider=provider,
        )
        return res
    except Exception as e:
        raise
