import secrets
import logging

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import APIKey
from app.utils.auth import hash_api_key, verify_master_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


class APIKeyResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime
    revoked_at: datetime | None = None

    class Config:
        from_attributes = True


@router.post("/keys/generate", response_model=dict)
async def generate_key(
    name: str,
    db: Session = Depends(get_db),
    _=Depends(verify_master_key)
):
    """Generate a new, unique API key."""
    # Create raw key (e.g. "sk_play_...")
    raw_key = f"sk_play_{secrets.token_urlsafe(32)}"
    hashed_key = hash_api_key(raw_key)

    new_key = APIKey(
        name=name,
        hashed_key=hashed_key,
        is_active=True
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    logger.info(f"Generated new API key: {name}")
    return {
        "api_key": raw_key, 
        "name": name,
        "note": "Save this key now — it cannot be recovered later."
    }


@router.get("/keys", response_model=list[APIKeyResponse])
async def list_keys(
    db: Session = Depends(get_db),
    _=Depends(verify_master_key)
):
    """List all registered API keys."""
    return db.query(APIKey).all()


@router.delete("/keys/{key_id}")
async def revoke_key(
    key_id: str,
    db: Session = Depends(get_db),
    _=Depends(verify_master_key)
):
    """Revoke (deactivate) an existing API key."""
    api_key_record = db.query(APIKey).filter(APIKey.id == key_id).first()
    
    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key not found.")

    api_key_record.is_active = False
    api_key_record.revoked_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"Revoked API key ID: {key_id}")
    return {"message": f"Successfully revoked key: {api_key_record.name}"}
