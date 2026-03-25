import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime

from app.db import Base

class APIKey(Base):
    __tablename__ = "playground_v1_api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, index=True)
    hashed_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)
