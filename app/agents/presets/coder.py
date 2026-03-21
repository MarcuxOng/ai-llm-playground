"""
A coding-focused ReAct agent.

Tools:
  • run_python_code  — run Python snippets in a sandboxed subprocess
  • calculate       — safe expression evaluator (no subprocess overhead)
  • read_file       — read a local file into context
  • write_file      — write content to a local file
  • test_regex      — validate and debug regular expressions
  • count_tokens     — count tokens in a string for a given model
"""

from app.agents.base import build_agent


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert Python developer and coding assistant.

Guidelines:
- Write clean, idiomatic Python 3.12+ code with type hints.
- Always test code using the run_python_code tool before presenting it as final.
- If execution raises an error, debug it — fix and re-run until it passes.
- Use calculate for quick maths; reserve run_python_code for real logic.
- Use read_file / write_file when the user wants to work with local files.
- Explain your reasoning briefly before presenting the final code.
"""

# ── Factory ───────────────────────────────────────────────────────────────────

TOOLS = [
    "run_python_code", 
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
        print(f"Error building coder agent: {e}")
        raise  
