import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.database.db import Base

class APIKey(Base):
    __tablename__ = "playground_v1_api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, index=True)
    hashed_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)


class Thread(Base):
    __tablename__ = "playground_v1_threads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True)
    preset = Column(String, nullable=False)
    model = Column(String, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    messages = relationship("ThreadMessage", back_populates="thread", order_by="ThreadMessage.created_at", cascade="all, delete-orphan", passive_deletes=True,)


class ThreadMessage(Base):
    __tablename__ = "playground_v1_thread_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("playground_v1_threads.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)   # "human" | "ai" | "tool"
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)    # raw tool call data if role=="ai"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    thread = relationship("Thread", back_populates="messages")


class Agents(Base):
    __tablename__ = "playground_v1_agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)   # slug, e.g. "my-coder"
    description = Column(String, nullable=True)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=False, default=list)   # list of tool name strings
    model = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))