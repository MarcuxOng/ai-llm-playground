# app/memory/checkpointer.py
import logging
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings

logger = logging.getLogger(__name__)

# Global instances to be reused and kept alive
_CHECKPOINTER = None
_CHECKPOINTER_CTX = None

def get_checkpointer():
    """
    Returns the appropriate LangGraph checkpointer based on DATABASE_URL.
    Handles the context manager returned by from_conn_string and ensures it stays alive.
    """
    global _CHECKPOINTER, _CHECKPOINTER_CTX
    if _CHECKPOINTER is not None:
        return _CHECKPOINTER

    db_url = settings.database_url
    # Clean logging for security
    logged_url = db_url.split('@')[-1] if '@' in db_url else db_url
    logger.info(f"Initializing checkpointer with database: {logged_url}")

    try:
        if db_url.startswith("sqlite"):
            db_path = db_url.replace("sqlite:///", "")
            # SqliteSaver.from_conn_string is a context manager
            _CHECKPOINTER_CTX = SqliteSaver.from_conn_string(db_path)
            _CHECKPOINTER = _CHECKPOINTER_CTX.__enter__()
        else:
            # PostgresSaver.from_conn_string is also a context manager
            _CHECKPOINTER_CTX = PostgresSaver.from_conn_string(db_url)
            _CHECKPOINTER = _CHECKPOINTER_CTX.__enter__()

        return _CHECKPOINTER
    except Exception as e:
        logger.error(f"Failed to initialize checkpointer: {e}")
        # Reset globals on failure
        _CHECKPOINTER = None
        _CHECKPOINTER_CTX = None
        raise