from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)


def gemini_service(prompt: str):
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        return response.text

    except Exception as e:
        raise e