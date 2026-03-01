import requests
import json

from app.config import settings


def openrouter_service(prompt: str):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": settings.openrouter_model,
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