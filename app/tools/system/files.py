"""
File tool — reads and writes local files.
"""

import logging
import os

from app.tools import register

logger = logging.getLogger(__name__)


@register
def read_file(path: str, max_chars: int = 4000) -> str:
    """
    Read the content of a local file.
    
    :param path: The path to the file to read (e.g., 'config.json').
    :param max_chars: Maximum characters to return (default 4000).
    """
    try:
        logger.info(f"Reading file: {path}")
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            return f"Error: File '{path}' not found."
            
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n[...Truncated to {max_chars} chars...]"
        return content
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return f"Error: {str(e)}"


@register
def write_file(path: str, content: str) -> str:
    """
    Write content to a local file.
    
    :param path: The path where to write the file.
    :param content: The text content to write.
    """
    try:
        logger.info(f"Writing file: {path}")
        abs_path = os.path.abspath(path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
        
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        logger.error(f"Error writing file {path}: {e}")
        return f"Error: {str(e)}"
