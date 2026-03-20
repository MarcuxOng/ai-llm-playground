"""
Web Scraper tool — fetches and extracts text from URLs.
"""

import logging
import requests
from bs4 import BeautifulSoup

from app.tools import register

logger = logging.getLogger(__name__)


@register
def scrape_url(url: str, max_chars: int = 4000) -> str:
    """
    Fetch a URL and extract clean text from it. 
    Use this when the user provides a direct link or you need more context than a search summary.

    :param url: The full URL to scrape (e.g., 'https://example.com').
    :param max_chars: The maximum amount of text to return (default 4000).
    """
    try:
        logger.info(f"Scraping URL: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script, style, and other noise
        for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
            tag.decompose()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        
        if not clean_text:
            return f"The URL {url} was fetched, but no readable text was found."

        # Limit response length
        if len(clean_text) > max_chars:
            return clean_text[:max_chars] + f"\n\n[...Truncated to {max_chars} chars...]"
            
        return clean_text

    except Exception as e:
        logger.error(f"Scraper error for {url}: {e}")
        return f"Error scraping the URL: {str(e)}"
