"""
A coding-focused ReAct agent.
"""

from typing import List
from langchain_core.tools import BaseTool

from app.agents.base import build_agent
from app.config import settings

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a senior software engineer and coding assistant.
You can write code in Python, JavaScript, Go, Rust, C++, and more.
"""

if settings.enable_execute_code:
    SYSTEM_PROMPT += "\nYou can execute code when needed.\n"
else:
    SYSTEM_PROMPT += "\nCode execution is currently disabled.\n"

SYSTEM_PROMPT += """
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

if settings.enable_execute_code:
    TOOLS.insert(0, "execute_code")


def build_coder_agent(
    model: str, 
    checkpointer=None,
    extra_tools: List[BaseTool] = None,
):
    """
    Build and return a coding ReAct agent.

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
