import logging
from google import genai
from langchain_core.embeddings import Embeddings
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddings(Embeddings):
    """
    LangChain compatible wrapper for Google Gemini Embeddings API.
    """
    def __init__(self, model: str = settings.gemini_embedding_model):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts,
                config={'task_type': 'retrieval_document'}
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config={'task_type': 'retrieval_query'}
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise
