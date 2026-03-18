import logging
import json
import requests

from app.config import settings

logger = logging.getLogger(__name__)

def list_openrouter_models():
    try: 
        logger.info("Fetching OpenRouter models...")
        URL = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
        }
        res = requests.get(URL, headers=headers)
        if res.status_code != 200:
            print("Failed to fetch models:", res.text)
            return

        models = res.json().get("data", [])
        free_models = sorted([m["id"] for m in models if m["id"].endswith(":free")])
        model_list = []
        for mid in free_models:
            model_list.append(mid)
        
        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        raise e


def openrouter_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with OpenRouter model: {model}")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

            })
        )

        data = response.json()
        output = data["choices"][0]["message"]["content"]
        return output

    except Exception as e:
        logger.error(f"Error in OpenRouter service: {e}")
        raise e