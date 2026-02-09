"""Conversation API schemas.

This module defines Pydantic schemas for conversation management
endpoints, including listing, retrieving, and deleting conversations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Enum for message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageSchema(BaseModel):
    """Schema for a single message in a conversation.

    Represents a message from the user, assistant, or system
    with optional tool call information.
    """
    id: int = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="ID of the parent conversation")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message text content")
    tool_calls: Optional[dict] = Field(None, description="Tool calls made in this message")
    created_at: datetime = Field(..., description="Message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Create a task to buy groceries",
                "tool_calls": None,
                "created_at": "2026-01-30T01:30:00Z"
            }
        }


class ConversationSchema(BaseModel):
    """Schema for a conversation summary.

    Used for listing conversations without loading all messages.
    """
    id: str = Field(..., description="Unique conversation identifier (UUID)")
    user_id: int = Field(..., description="ID of the user who owns this conversation")
    title: Optional[str] = Field(None, description="Conversation title (auto-generated)")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last message timestamp")
    message_count: int = Field(0, description="Number of messages in this conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": 1,
                "title": "Task management conversation",
                "created_at": "2026-01-30T01:30:00Z",
                "updated_at": "2026-01-30T01:35:00Z",
                "message_count": 5
            }
        }


class ConversationDetailSchema(ConversationSchema):
    """Schema for a conversation with full message history.

    Extends ConversationSchema to include all messages in the conversation.
    """
    messages: List[MessageSchema] = Field(
        default_factory=list,
        description="List of all messages in the conversation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": 1,
                "title": "Task management conversation",
                "created_at": "2026-01-30T01:30:00Z",
                "updated_at": "2026-01-30T01:35:00Z",
                "messages": [
                    {
                        "id": 1,
                        "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                        "role": "user",
                        "content": "Create a task to buy groceries",
                        "tool_calls": None,
                        "created_at": "2026-01-30T01:30:00Z"
                    },
                    {
                        "id": 2,
                        "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                        "role": "assistant",
                        "content": "I've created a task for you: 'Buy groceries'.",
                        "tool_calls": {"create_task": {"title": "Buy groceries"}},
                        "created_at": "2026-01-30T01:30:05Z"
                    }
                ]
            }
        }


class ConversationListResponse(BaseModel):
    """Response schema for listing conversations.

    Includes pagination metadata and list of conversations.
    """
    conversations: List[ConversationSchema] = Field(
        default_factory=list,
        description="List of conversations"
    )
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Number of conversations per page")
    offset: int = Field(..., description="Offset for pagination")

    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": 1,
                        "title": "Task management",
                        "created_at": "2026-01-30T01:30:00Z",
                        "updated_at": "2026-01-30T01:35:00Z"
                    }
                ],
                "total": 1,
                "limit": 20,
                "offset": 0
            }
        }
