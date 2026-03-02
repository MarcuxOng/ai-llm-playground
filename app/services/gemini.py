from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)


def list_gemini_models():
    try:
        models = sorted(client.models.list(), key=lambda m: m.name)
        model_list = []
        for m in models:
            response = m.name.replace("models/", "")
            model_list.append(response)
    
        return model_list
    
    except Exception as e:
        raise e


def gemini_service(model: str, prompt: str):
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text

    except Exception as e:
        raise e