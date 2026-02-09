"""ToolInvocation database model."""
from sqlmodel import SQLModel, Field, Relationship, Index, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message
    from .conversation import Conversation
    from .user import User


class ToolInvocation(SQLModel, table=True):
    """ToolInvocation model for audit logging of tool executions.

    Tracks all tool invocations for debugging, analytics, and compliance.
    Each invocation is linked to a message, conversation, and user.
    """

    __tablename__ = "tool_invocations"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="messages.id", nullable=False, index=True)
    conversation_id: str = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        max_length=36
    )
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    tool_name: str = Field(max_length=100, nullable=False)
    tool_arguments: dict = Field(sa_column=Column(JSON, nullable=False))
    tool_result: dict = Field(sa_column=Column(JSON, nullable=False))
    success: bool = Field(nullable=False)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    execution_time_ms: int = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    message: Optional["Message"] = Relationship(back_populates="tool_invocations")
    conversation: Optional["Conversation"] = Relationship(back_populates="tool_invocations")
    user: Optional["User"] = Relationship(back_populates="tool_invocations")

    # Composite index for tool usage analytics
    __table_args__ = (
        Index("ix_tool_invocations_tool_created", "tool_name", "created_at"),
    )
