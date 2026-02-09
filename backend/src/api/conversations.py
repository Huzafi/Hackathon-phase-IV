"""Conversation management API endpoints.

This module implements endpoints for:
- Listing user's conversations
- Retrieving a specific conversation with messages
- Deleting a conversation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List

from ..core.database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.tool_invocation import ToolInvocation
from ..schemas.conversation import (
    ConversationSchema,
    ConversationDetailSchema,
    ConversationListResponse,
    MessageSchema,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100, description="Number of conversations per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ConversationListResponse:
    """List all conversations for the authenticated user.

    Returns conversations ordered by most recent activity (updated_at DESC).
    Supports pagination with limit and offset parameters.
    Includes message_count for each conversation.

    Args:
        limit: Maximum number of conversations to return (1-100)
        offset: Number of conversations to skip
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ConversationListResponse with list of conversations and pagination metadata
    """
    # Get total count
    count_statement = (
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    )
    total = session.exec(count_statement).one()

    # Get conversations
    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    conversations = session.exec(statement).all()

    # Build response with message counts
    conversation_schemas = []
    for conv in conversations:
        # Count messages for this conversation
        message_count_statement = (
            select(func.count(Message.id))
            .where(Message.conversation_id == conv.id)
        )
        message_count = session.exec(message_count_statement).one()

        conversation_schemas.append(
            ConversationSchema(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count,
            )
        )

    return ConversationListResponse(
        conversations=conversation_schemas,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ConversationDetailSchema:
    """Get a specific conversation with all messages.

    Loads the conversation and all its messages ordered by creation time.
    Verifies that the conversation belongs to the authenticated user.

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ConversationDetailSchema with conversation metadata and all messages

    Raises:
        HTTPException 404: Conversation not found or doesn't belong to user
    """
    # Load conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Verify ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Load messages
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(statement).all()

    return ConversationDetailSchema(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageSchema(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a conversation and all its messages and tool invocations.

    Permanently deletes the conversation and all associated messages and tool_invocations.
    Verifies that the conversation belongs to the authenticated user.
    Cascade delete order: tool_invocations -> messages -> conversation

    Args:
        conversation_id: UUID of the conversation to delete
        current_user: Authenticated user from JWT token
        session: Database session

    Raises:
        HTTPException 404: Conversation not found or doesn't belong to user
    """
    # Load conversation
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Verify ownership (return 404 to prevent information leakage)
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete tool_invocations first (they reference messages and conversation)
    tool_invocation_statement = select(ToolInvocation).where(
        ToolInvocation.conversation_id == conversation_id
    )
    tool_invocations = session.exec(tool_invocation_statement).all()
    for tool_invocation in tool_invocations:
        session.delete(tool_invocation)

    # Delete all messages (they reference conversation)
    message_statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(message_statement).all()
    for message in messages:
        session.delete(message)

    # Finally delete conversation
    session.delete(conversation)
    session.commit()
