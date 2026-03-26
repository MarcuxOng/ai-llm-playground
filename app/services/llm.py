import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def build_llm(provider: str, model_name: str, temperature: float = 0.1):
    logger.info(f"Building LLM for provider: {provider}, model: {model_name}")
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model_name, 
            google_api_key=settings.gemini_api_key, 
            temperature=temperature
        )
    elif provider == "groq":
        return ChatGroq(
            model=model_name, 
            api_key=settings.groq_api_key, 
            temperature=temperature
        )
    elif provider == "mistral":
        return ChatMistralAI(
            model=model_name, 
            api_key=settings.mistral_api_key, 
            temperature=temperature
        )
    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name, 
            openai_api_key=settings.openrouter_api_key, 
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature
        )
    else:
        logger.error(f"Unsupported provider: {provider}")
        raise ValueError(f"Unsupported provider: {provider}")