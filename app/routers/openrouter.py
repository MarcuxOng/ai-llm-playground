from fastapi import APIRouter
from pydantic import BaseModel

from app.services.openrouter import (
    list_openrouter_models,
    openrouter_service
)

router = APIRouter(prefix="/openrouter", tags=["OpenRouter"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/openrouter")
async def get_openrouter_model():
    return list_openrouter_models()


@router.post("/openrouter")
async def openrouter(request: ProviderInput):
    response = openrouter_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response