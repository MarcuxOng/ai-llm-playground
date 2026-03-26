"""
Core graph builder. All agent presets call build_agent() to
get a compiled LangGraph ReAct graph wired to a provider-specific LLM.
"""

import logging
from typing import List, Union

from langchain_core.tools import BaseTool, StructuredTool
from langgraph.prebuilt import create_react_agent

from app.services.llm import build_llm
from app.tools import _REGISTRY

logger = logging.getLogger(__name__)


def project_tools_to_langchain(tool_names: List[str]) -> List[BaseTool]:
    """
    Convert project-specific registered tools to LangChain-compatible BaseTools.
    
    Args:
        tool_names: List of tool names as registered in the project's tool registry.
        
    Returns:
        List of LangChain BaseTool objects.
    """
    lc_tools = []
    missing_tools: List[str] = []
    for name in tool_names:
        entry = _REGISTRY.get(name)
        if not entry:
            missing_tools.append(name)
            continue
        
        fn = entry["fn"]
        schema = entry["schema"]
        
        # Create a LangChain tool from the function
        lc_tool = StructuredTool.from_function(
            func=fn,
            name=name,
            description=schema["function"]["description"]
        )
        lc_tools.append(lc_tool)
        
    if missing_tools:
        raise ValueError(f"Tool(s) not found in registry: {missing_tools}")
    return lc_tools


def build_agent(
    tools: Union[List[BaseTool], List[str]],
    system_prompt: str,
    model: str,
    provider: str,
):
    """
    Build and return a compiled LangGraph ReAct agent.

    Args:
        tools:         List of LangChain tools OR list of project tool names.
        system_prompt: System-level instruction injected at the start of every run.
        model:         Model name.
        provider:      Provider name ('gemini', 'groq', 'mistral', 'openrouter').

    Returns:
        A compiled LangGraph CompiledGraph ready to invoke.
    """
    try:
        # Convert string tool names to LangChain tools if needed
        processed_tools = []
        if tools and isinstance(tools[0], str):
            processed_tools = project_tools_to_langchain(tools)
        else:
            processed_tools = tools

        llm = create_react_agent(
            model=build_llm(provider, model),
            tools=processed_tools,
            prompt=system_prompt,
        )
        return llm
    except Exception as e:
        logger.error(f"Error building agent: {e}")
        raise
