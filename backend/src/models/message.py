"""Message database model."""
from sqlmodel import SQLModel, Field, Relationship, Index, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation
    from .tool_invocation import ToolInvocation


class MessageRole(str, Enum):
    """Enum for message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message model for conversation messages.

    Represents a single message in a conversation from user, assistant, or system.
    Assistant messages may include tool calls that are tracked separately.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        max_length=36
    )
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    tool_invocations: List["ToolInvocation"] = Relationship(back_populates="message")

    # Composite index for efficient message loading within conversations
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
