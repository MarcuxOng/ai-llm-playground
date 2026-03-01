from fastapi import APIRouter

from app.services.gemini import gemini_service
from app.services.groq import groq_service
from app.services.mistral import mistral_service
from app.services.openrouter import openrouter_service

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/gemini")
async def gemini(prompt: str):
    response = gemini_service(prompt)

    return response


@router.get("/groq")
async def groq(prompt: str):
    response = groq_service(prompt)

    return response


@router.get("/mistral")
async def mistral(prompt: str):
    response = mistral_service(prompt)

    return response


@router.get("/openrouter")
async def openrouter(prompt: str):
    response = openrouter_service(prompt)

    return response