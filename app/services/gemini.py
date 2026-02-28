from google import genai
from google.genai import types

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)


def gemini_service(prompt):
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )

    return response.text