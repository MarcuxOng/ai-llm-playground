import logging
import requests
from mistralai import Mistral

from app.config import settings

logger = logging.getLogger(__name__)

def list_mistral_models():
    try:
        logger.info("Fetching Mistral models...")
        url = "https://api.mistral.ai/v1/models"
        headers = {
            "Authorization": f"Bearer {settings.mistral_api_key}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        models = result.get("data", [])
        ids = sorted([m["id"] for m in models])
        model_list = []

        for mid in ids:
            model_list.append(mid)

        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching Mistral models: {e}")
        raise e


def mistral_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with Mistral model: {model}")
        with Mistral(
            api_key=settings.mistral_api_key,
        ) as mistral:
            res = mistral.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                stream=False
            )

            response = res.choices[0].message.content

        return response

    except Exception as e:
        logger.error(f"Error generating content with Mistral: {e}")
        raise e