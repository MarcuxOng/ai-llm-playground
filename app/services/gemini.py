from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from google import genai
from google.genai import types

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


def structured_service(model: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    """
    Structured output service using raw genai.Client.
    Returns guaranteed-valid JSON matching the provided schema.
    """
    try:
        logger.info(f"Generating structured content with Gemini model: {model}")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        # Parse the JSON string into a dict
        return dict(json.loads(response.text))

    except Exception as e:
        logger.error(f"Error generating structured content: {e}")
        raise


def generate_thread_title(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Generates a short (3-5 words) descriptive title for a thread based on the initial prompt.
    """
    try:
        logger.info("Generating thread title...")
        # Use a concise internal prompt for title generation
        title_prompt = (
            f"Generate a concise, 3-5 word title for a conversation that starts with: '{prompt}'. "
            "Respond ONLY with the title text, no quotes or punctuation."
        )
        llm = build_llm(model)
        response = llm.invoke(title_prompt)
        title = str(response.content).strip()
        # Clean up any quotes if the model ignored instructions
        return title.replace('"', "").replace("'", "")
    except Exception as e:
        logger.error(f"Error generating thread title: {e}")
        # Fallback to a truncated version of the prompt if LLM fails
        return prompt[:30] + "..." if len(prompt) > 30 else prompt


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
