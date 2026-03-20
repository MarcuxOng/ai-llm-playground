from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mistral import (
    list_mistral_models, 
    mistral_service
)

router = APIRouter(prefix="/mistral", tags=["Mistral"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/mistral")
async def get_mistral_model():
    return list_mistral_models()


@router.post("/")
async def mistral(request: ProviderInput):
    response = mistral_service(
        model=request.model,
        prompt=request.prompt
    )

    return response