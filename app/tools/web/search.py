"""
Search tool — searches the web using DuckDuckGo.
"""

import logging
import requests

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
        logger.info(f"Searching web for: {query}")
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"},
        )
        r.raise_for_status()
        data = r.json()
        
        results = []
        
        # Abstract (top answer)
        if data.get("AbstractText"):
            results.append(f"Title: {data.get('Heading', 'Summary')}\nURL: {data.get('AbstractURL', '')}\nSnippet: {data['AbstractText']}")

        # Related topics
        for topic in data.get("RelatedTopics", []):
            if len(results) >= max_results:
                break
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"Title: {topic.get('Text', '')[:80]}\nURL: {topic.get('FirstURL', '')}\nSnippet: {topic.get('Text', '')}")

        if not results:
            return f"No results found for '{query}'."

        return "\n\n---\n\n".join(results)
    except Exception as e:
        logger.error(f"Web search error for {query}: {e}")
        return f"Error: {str(e)}"
