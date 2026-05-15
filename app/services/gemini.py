from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from google import genai

from app.config import settings
from app.services.llm import build_llm

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.gemini_api_key)


def list_gemini_models() -> list[str]:
    try:
        logger.info("Fetching Gemini models...")
        models = sorted(client.models.list(), key=lambda m: m.name or "")
        model_list: list[str] = []
        for m in models:
            if m.name:
                response = m.name.replace("models/", "")
                model_list.append(response)

        return model_list

    except Exception as e:
        logger.error(f"Error fetching Gemini models: {e}")
        raise


def gemini_service(model: str, prompt: str) -> str:
    """Generation service consolidated on the LangChain path."""
    try:
        logger.info(f"Generating content with Gemini model: {model}")
        llm = build_llm(model)
        response = llm.invoke(prompt)
        return str(response.content)

    except Exception as e:
        logger.error(f"Error generating Gemini content: {e}")
        raise


async def gemini_stream_service(model: str, prompt: str) -> AsyncGenerator[str, None]:
    """Streaming intentionally uses genai.Client.aio for native SSE support."""
    try:
        logger.info(f"Starting Gemini streaming generation with model: {model}")
        async with client.aio as async_client:
            response = await async_client.models.generate_content_stream(
                model=model, contents=prompt
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
    except Exception as e:
        logger.error(f"Error in Gemini streaming service: {e}")
        raise
