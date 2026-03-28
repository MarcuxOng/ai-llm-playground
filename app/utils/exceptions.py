from fastapi import Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail, 
            "path": str(request.url)
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": f"Internal server error - {exc}", 
            "path": str(request.url)
        }
    )