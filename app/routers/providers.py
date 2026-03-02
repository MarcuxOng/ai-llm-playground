from fastapi import APIRouter
from pydantic import BaseModel

from app.services.gemini import gemini_service
from app.services.groq import groq_service
from app.services.mistral import mistral_service
from app.services.openrouter import openrouter_service

router = APIRouter(prefix="/providers", tags=["Providers"])

class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.post("/gemini")
async def gemini(request: ProviderInput):
    response = gemini_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/groq")
async def groq(request: ProviderInput):
    response = groq_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/mistral")
async def mistral(request: ProviderInput):
    response = mistral_service(
        model=request.model,
        prompt=request.prompt
    )

    return response


@router.post("/openrouter")
async def openrouter(request: ProviderInput):
    response = openrouter_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response