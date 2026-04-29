"""
Converts external MCP server configs into LangChain-compatible tools
using langchain-mcp-adapters.
"""
import logging
from typing import List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


async def load_mcp_tools(server_config: dict) -> List[BaseTool]:
    """
    Connect to an external MCP server and return its tools as LangChain BaseTools.
    """
    try:
        transport = server_config.get("transport")
        
        # Infer transport if missing
        if not transport:
            if server_config.get("url"):
                transport = "sse"
            elif server_config.get("command"):
                transport = "stdio"
            else:
                raise ValueError(f"Could not infer transport for MCP server '{server_config.get('name')}'. Provide 'url' or 'command'.")

        if transport == "sse":
            servers = {
                server_config["name"]: {
                    "transport": "sse",
                    "url": server_config["url"],
                }
            }
        elif transport == "stdio":
            servers = {
                server_config["name"]: {
                    "transport": "stdio",
                    "command": server_config["command"],
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {}),
                }
            }
        else:
            raise ValueError(f"Unsupported MCP transport: {transport}")

        async with MultiServerMCPClient(servers) as client:
            tools = client.get_tools()
            logger.info(f"Loaded {len(tools)} tools from MCP server '{server_config['name']}'")
            return tools

    except ImportError:
        logger.error("langchain-mcp-adapters not installed. Run: pip install langchain-mcp-adapters")
        return []
    except Exception as e:
        logger.error(f"Failed to load MCP tools from '{server_config.get('name')}': {e}")
        return []