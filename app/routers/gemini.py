from fastapi import APIRouter
from pydantic import BaseModel

from app.services.gemini import (
    gemini_service, 
    list_gemini_models, 
    # tools_service
)

router = APIRouter(prefix="/gemini", tags=["Gemini"])


class ProviderInput(BaseModel):
    model: str
    prompt: str


@router.get("/models")
async def get_gemini_model():
    return list_gemini_models()


@router.post("/")
async def gemini(request: ProviderInput):
    response = gemini_service(
        model=request.model, 
        prompt=request.prompt
    )

    return response


# @router.post("/tools")
# async def tools(request: ProviderInput):
#     """
#     Gemini with tool calling support.

#     Tools consist of:
#         - calculate: Evaluate mathematical expressions with support for common operators and functions.
#         - python_runner: Execute Python code snippets for data analysis, algorithms, or logic verification.
#         - web_search: Perform web searches to retrieve current information.
#     """
#     response = tools_service(
#         model=request.model, 
#         prompt=request.prompt
#     )

#     return response