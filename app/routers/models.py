from fastapi import APIRouter

from app.services.gemini import list_gemini_models
from app.services.groq import get_groq_models
from app.services.mistral import list_mistral_models
from app.services.openrouter import list_openrouter_models

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/gemini")
async def get_gemini_model():
    return list_gemini_models()


@router.get("/groq")
async def get_groq_model():
    return get_groq_models()


@router.get("/mistral")
async def get_mistral_model():
    return list_mistral_models()


@router.get("/openrouter")
async def get_openrouter_model():
    return list_openrouter_models()