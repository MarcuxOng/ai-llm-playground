from mistralai import Mistral

from app.config import settings


def mistral_service(prompt: str):
    try:
        with Mistral(
            api_key=settings.mistral_api_key,
        ) as mistral:
            res = mistral.chat.complete(
                model=settings.mistral_model,
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
        raise e