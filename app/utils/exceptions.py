import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception for {request.url}: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,  
            "path": str(request.url)
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception for {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "path": str(request.url)
        }
    )