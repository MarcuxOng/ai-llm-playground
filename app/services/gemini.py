import logging
from google import genai

from app.config import settings

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.gemini_api_key)


def list_gemini_models():
    try:
        logging.info("Fetching Gemini models...")
        models = sorted(client.models.list(), key=lambda m: m.name)
        model_list = []
        for m in models:
            response = m.name.replace("models/", "")
            model_list.append(response)
    
        return model_list
    
    except Exception as e:
        logging.error(f"Error fetching Gemini models: {e}")
        raise e


def gemini_service(model: str, prompt: str):
    try:
        logging.info(f"Generating content with Gemini model: {model}")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text

    except Exception as e:
        logging.error(f"Error generating Gemini content: {e}")
        raise e