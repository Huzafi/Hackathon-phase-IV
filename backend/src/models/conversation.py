"""Conversation database model."""
from sqlmodel import SQLModel, Field, Relationship, Index
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from .user import User
    from .message import Message
    from .tool_invocation import ToolInvocation


class Conversation(SQLModel, table=True):
    """Conversation model for AI agent chat sessions.

    Represents a chat conversation between a user and the AI agent.
    Each conversation contains multiple messages and tracks tool invocations.
    """

    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        max_length=36
    )
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    tool_invocations: List["ToolInvocation"] = Relationship(back_populates="conversation")

    # Composite index for efficient user-scoped queries sorted by recent activity
    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )
