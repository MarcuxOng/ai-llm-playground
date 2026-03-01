from groq import Groq
from groq.types.chat import ChatCompletionUserMessageParam

from app.config import settings

client = Groq(api_key=settings.groq_api_key)


def groq_service(prompt: str):
    try:
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.6,
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
        return e