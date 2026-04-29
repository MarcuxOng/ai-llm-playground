"""
FastMCP server that exposes all registered tools to any MCP-compatible client.
Tools are pulled dynamically from the project's tool registry so there is
no duplication — adding a tool to the registry automatically exposes it here.
"""

import logging
import secrets
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.database.db import SessionLocal
from app.tools import _REGISTRY
from app.utils.auth import check_api_key

logger = logging.getLogger(__name__)
# ... (mcp initialization unchanged)

class MCPAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # FastMCP SSE transport passes through HTTP headers
        if request.url.path.startswith("/mcp"):
            api_key = request.headers.get("x-api-key")
            if not api_key:
                return JSONResponse({"error": "Unauthorized: Missing API Key"}, status_code=401)
            
            db = SessionLocal()
            try:
                if check_api_key(api_key, db):
                    return await call_next(request)
            finally:
                db.close()
                
            return JSONResponse({"error": "Unauthorized: Invalid API Key"}, status_code=401)
        return await call_next(request)


def _register_all_tools():
    """Dynamically register every tool in the project registry with FastMCP."""
    failures = []
    for tool_name, entry in _REGISTRY.items():
        fn = entry["fn"]

        try:
            mcp.tool(name=tool_name)(fn)
            logger.info(f"MCP: registered tool '{tool_name}'")
        except Exception as e:
            logger.exception("MCP: could not register tool '%s'", tool_name)
            failures.append(tool_name)

    if failures:
        raise RuntimeError(f"Failed to register MCP tools: {failures}")

_register_all_tools()