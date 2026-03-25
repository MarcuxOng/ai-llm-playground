import logging
import hashlib

from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import APIKey


logger = logging.getLogger(__name__)

def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256 for secure DB lookup."""
    return hashlib.sha256(api_key.encode()).hexdigest()


async def verify_api_key(
    x_api_key: str = Header(...), 
    db: Session = Depends(get_db)
):
    """
    Dependency to verify API keys by hashing and checking the DB.
    Fallbacks to master_api_key for initial admin setup.
    """
    # 1. Check Master Key
    if x_api_key == settings.master_api_key:
        return x_api_key

    # 2. Check Database Keys
    hashed = hash_api_key(x_api_key)
    api_key_record = db.query(APIKey).filter(
        APIKey.hashed_key == hashed,
        APIKey.is_active == True
    ).first()

    if not api_key_record:
        logger.warning("Unauthorized API access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    
    return x_api_key


async def verify_master_key(x_api_key: str = Header(...)):
    """
    Dependency that only allows requests using the MASTER_API_KEY.
    Used for administrative endpoints like creating/listing keys.
    """
    if x_api_key != settings.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrative privileges required."
        )