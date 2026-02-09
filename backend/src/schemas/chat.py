"""Chat API request/response schemas.

This module defines Pydantic schemas for the chat endpoint,
including request validation and response formatting.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolCallSchema(BaseModel):
    """Schema for a single tool invocation within a message.

    Represents a tool call made by the AI agent, including
    the tool name, arguments, and result.
    """
    id: str = Field(..., description="Unique identifier for this tool call")
    name: str = Field(..., description="Name of the tool invoked")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the tool")
    result: Optional[Dict[str, Any]] = Field(None, description="Result returned by the tool")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "call_abc123",
                "name": "create_task",
                "arguments": {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread"
                },
                "result": {
                    "success": True,
                    "message": "Task created successfully",
                    "data": {
                        "task_id": 123
                    }
                }
            }
        }


class ChatRequest(BaseModel):
    """Request schema for sending a message to the AI agent.

    The conversation_id is optional - if not provided, a new
    conversation will be created.
    """
    conversation_id: Optional[str] = Field(
        None,
        description="ID of existing conversation (omit to start new conversation)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message to send to the agent"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Create a task to buy groceries"
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint.

    Contains the agent's response message, conversation ID,
    and any tool calls that were made.
    """
    conversation_id: str = Field(..., description="ID of the conversation")
    message: str = Field(..., description="Agent's response message")
    tool_calls: Optional[List[ToolCallSchema]] = Field(
        None,
        description="List of tool calls made by the agent"
    )
    created_at: datetime = Field(..., description="Timestamp of the response")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I've created a task for you: 'Buy groceries'. Would you like to add any details?",
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "name": "create_task",
                        "arguments": {
                            "title": "Buy groceries"
                        },
                        "result": {
                            "success": True,
                            "task_id": 123
                        }
                    }
                ],
                "created_at": "2026-01-30T01:30:00Z"
            }
        }
