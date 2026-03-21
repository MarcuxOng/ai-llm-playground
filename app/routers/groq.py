from fastapi import APIRouter
from pydantic import BaseModel

from app.services.groq import (
    get_groq_models, 
    groq_service
)

router = APIRouter(prefix="/groq", tags=["Groq"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_groq_model():
    return get_groq_models()


@router.post("/")
async def groq(request: ProviderInput):
    response = groq_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


@router.post("/tools")
async def tools(request: ProviderInput):
    """
    Groq with tool calling support.
    """
    return {"message": "Groq tool calling is not implemented yet."}