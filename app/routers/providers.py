from fastapi import APIRouter

from app.services.gemini import gemini_service

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.get("/gemini")
async def gemini(prompt: str):
    response = gemini_service(prompt)

    return response