"""
Web Scraper tool — fetches and extracts text from URLs.
"""

import logging
import requests
import socket
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.tools import register

logger = logging.getLogger(__name__)

def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe to fetch (prevents SSRF).
    Blocks private IP ranges, localhost, and non-http/https protocols.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IP
        ip_address = socket.gethostbyname(hostname)
        
        # Check for private/reserved IP ranges
        # 127.0.0.0/8 (Loopback)
        # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (Private)
        # 169.254.0.0/16 (Link-local)
        ip_parts = list(map(int, ip_address.split('.')))
        
        if ip_parts[0] == 127: return False
        if ip_parts[0] == 10: return False
        if ip_parts[0] == 172 and (16 <= ip_parts[1] <= 31): return False
        if ip_parts[0] == 192 and ip_parts[1] == 168: return False
        if ip_parts[0] == 169 and ip_parts[1] == 254: return False
        
        return True
    except Exception:
        return False


@register
def scrape_url(url: str, max_chars: int = 4000) -> str:
    """
    Fetch a URL and extract clean text from it. 
    Use this when the user provides a direct link or you need more context than a search summary.

    :param url: The full URL to scrape (e.g., 'https://example.com').
    :param max_chars: The maximum amount of text to return (default 4000).
    """
    try:
        if not is_safe_url(url):
            return f"Error: The URL '{url}' is restricted for security reasons (SSRF protection)."

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
