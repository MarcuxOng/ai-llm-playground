import json
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.utils.auth import verify_api_key
from app.services.gemini import (
    gemini_service, 
    list_gemini_models, 
    tools_service,
    gemini_stream_service
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/gemini", 
    tags=["Gemini"],
    dependencies=[Depends(verify_api_key)]
)


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_gemini_model():
    logger.info("Fetching available Gemini models")
    return list_gemini_models()


@router.post("/")
async def gemini(request: ProviderInput):
    logger.info(f"Calling Gemini API with model: {request.model}, prompt: {request.prompt}")
    response = gemini_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    Gemini with tool calling support.
    """
    logger.info(f"Calling Gemini tools with model: {request.model}, prompt: {request.prompt}")
    response = tools_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/stream")
async def gemini_stream(request: ProviderInput):
    """
    Stream Gemini response
    """
    logger.info(f"Starting Gemini stream with model: {request.model}, prompt: {request.prompt}")
    async def event_generator():
        async for chunk in gemini_stream_service(
            request.model, 
            request.prompt
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")