import requests
import json

from app.config import settings


def list_openrouter_models():
    try: 
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
        raise e


def openrouter_service(model: str, prompt: str):
    try:
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
        raise e