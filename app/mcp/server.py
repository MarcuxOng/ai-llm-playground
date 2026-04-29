"""
FastMCP server that exposes all registered tools to any MCP-compatible client.
Tools are pulled dynamically from the project's tool registry so there is
no duplication — adding a tool to the registry automatically exposes it here.
"""

import logging
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.database.db import SessionLocal
from app.database.models import APIKey
from app.tools import _REGISTRY
from app.utils.auth import hash_api_key 

logger = logging.getLogger(__name__)
mcp = FastMCP(
    name="ai-llm-playground",
    instructions="An AI platform exposing tools",
)


class MCPAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # FastMCP SSE transport passes through HTTP headers
        if request.url.path.startswith("/mcp"):
            api_key = request.headers.get("x-api-key")
            
            # Check Master Key
            if api_key and settings.master_api_key and api_key == settings.master_api_key:
                return await call_next(request)
            
            # Check Database Keys
            if api_key:
                db = SessionLocal()
                try:
                    hashed = hash_api_key(api_key)
                    api_key_record = db.query(APIKey).filter(
                        APIKey.hashed_key == hashed,
                        APIKey.is_active == True
                    ).first()
                    
                    if api_key_record:
                        return await call_next(request)
                finally:
                    db.close()
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
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