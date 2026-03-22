from fastapi import APIRouter
from pydantic import BaseModel

from app.services.openrouter import (
    list_openrouter_models,
    openrouter_service,
    tools_service
)

router = APIRouter(prefix="/openrouter", tags=["OpenRouter"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/openrouter")
async def get_openrouter_model():
    return list_openrouter_models()


@router.post("/")
async def openrouter(request: ProviderInput):
    response = openrouter_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    OpenRouter with tool calling support.
    """
    response = tools_service(
        model=request.model,
        prompt=request.prompt
    )
    return response