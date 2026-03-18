import logging
import requests
from groq import Groq
from groq.types.chat import ChatCompletionUserMessageParam

from app.config import settings

logger = logging.getLogger(__name__)
client = Groq(api_key=settings.groq_api_key)


def get_groq_models():
    try:
        logger.info("Fetching Groq models...")
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        models = response.raise_for_status().json()
        model_ids = [model['id'] for model in models['data']]
        model_list = []
        for model_id in sorted(model_ids):
            model_list.append(model_id)

        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching Groq models: {e}")
        return e


def groq_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with Groq model: {model}")
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None
        )

        response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                response += content

        return response

    except Exception as e:
        logger.error(f"Error generating content with Groq: {e}")
        return e