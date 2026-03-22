"""
Search tool — searches the web using the official Google Custom Search API.
"""

import logging
from googleapiclient.discovery import build

from app.config import settings
from app.tools import register

logger = logging.getLogger(__name__)


@register
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for a given query and return a summary of results.
    
    :param query: The search query (e.g., 'Latest AI news').
    :param max_results: Maximum number of results to return (default 5).
    """
    try:
        logger.info(f"Searching Google for: {query}")
        
        # Build the service
        service = build(
            "customsearch", 
            "v1", 
            developerKey=settings.google_search_api_key
        )
    
        # Execute the search
        res = service.cse().list(
            q=query, 
            cx=settings.google_cse_id, 
            num=min(max_results, 10)
        ).execute()

        items = res.get('items', [])
        if not items:
            return f"No Google results found for '{query}'."
        
        results = []
        for item in items:
            title = item.get('title', 'No Title')
            link = item.get('link', '#')
            snippet = item.get('snippet', 'No snippet available.')
            results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}")

        return "\n\n---\n\n".join(results)
    except Exception as e:
        logger.error(f"Google web search error for {query}: {e}")
        return f"Error performing Google Search: {str(e)}"
