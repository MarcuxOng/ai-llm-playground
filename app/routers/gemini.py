from fastapi import APIRouter

from app.services.gemini import gemini_service

router = APIRouter(prefix="/gemini", tags=["Gemini"])

@router.get("/")
async def gemini(prompt: str):
    response = gemini_service(prompt)

    return response