"""Chat API endpoint for AI agent interactions.

This module implements the stateless chat endpoint that:
1. Loads or creates conversations
2. Saves user messages
3. Loads conversation history
4. Invokes the AI agent
5. Saves assistant responses
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict, Any, List
from datetime import datetime
import json
import time

from ..core.database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..models.tool_invocation import ToolInvocation
from ..schemas.chat import ChatRequest, ChatResponse, ToolCallSchema
from ..agent import invoke_agent

router = APIRouter(prefix="/chat", tags=["chat"])


def generate_conversation_title(message: str, max_length: int = 50) -> str:
    """Generate a conversation title from the first user message.

    Args:
        message: The first user message
        max_length: Maximum length of the title

    Returns:
        A truncated version of the message suitable as a title
    """
    # Remove extra whitespace and newlines
    title = " ".join(message.split())

    # Truncate if too long
    if len(title) > max_length:
        title = title[:max_length].rsplit(' ', 1)[0] + "..."

    return title


def log_tool_invocation(
    session: Session,
    message_id: int,
    conversation_id: str,
    user_id: int,
    tool_call: Dict[str, Any],
    execution_time_ms: int,
) -> None:
    """Log a tool invocation to the database for audit and analytics.

    Args:
        session: Database session
        message_id: ID of the message that triggered the tool
        conversation_id: ID of the conversation
        user_id: ID of the user
        tool_call: Tool call data with name, arguments, and result
        execution_time_ms: Execution time in milliseconds
    """
    try:
        # Parse tool result to determine success
        result = tool_call.get("result", {})
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = {"raw": result}

        success = result.get("success", False) if isinstance(result, dict) else False
        error_message = result.get("error") if isinstance(result, dict) else None

        # Create tool invocation record
        invocation = ToolInvocation(
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
            tool_name=tool_call.get("name", "unknown"),
            tool_arguments=tool_call.get("arguments", {}),
            tool_result=result,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
        )

        session.add(invocation)
        session.commit()
    except Exception as e:
        # Don't let logging failures block the main flow
        print(f"Failed to log tool invocation: {str(e)}")
        session.rollback()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChatResponse:
    """Send a message to the AI agent and get a response.

    This endpoint:
    1. Creates a new conversation if conversation_id is not provided
    2. Saves the user's message to the database
    3. Loads the conversation history (last 20 messages)
    4. Invokes the AI agent with full context
    5. Saves the assistant's response to the database
    6. Returns the response with conversation_id and tool calls

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatResponse with agent's message, conversation_id, and tool calls

    Raises:
        HTTPException 404: Conversation not found or doesn't belong to user
        HTTPException 500: Agent invocation or database error
    """
    try:
        # Step 1: Load or create conversation
        if request.conversation_id:
            # Load existing conversation
            conversation = session.get(Conversation, request.conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            if conversation.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this conversation"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=None,  # Will be auto-generated from first message
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Step 2: Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )
        session.add(user_message)
        session.commit()

        # Step 3: Load conversation history (last 20 messages)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        messages = session.exec(statement).all()
        messages.reverse()  # Oldest first for agent context

        # Format messages for agent
        agent_messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in messages
        ]

        # Step 4: Invoke agent with full context
        start_time = time.time()
        agent_response = invoke_agent(
            messages=agent_messages,
            user_id=current_user.id,
            #session=session,
        )
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Extract assistant message from agent response
        # The agent returns a list of messages, we want the last one (assistant's response)
        response_messages = agent_response.get("messages", [])
        if not response_messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent returned no response"
            )

        # Get the last message (assistant's response)
        last_message = response_messages[-1]
        assistant_content = last_message.get("content", "")

        # Extract tool calls if present
        tool_calls_data = None
        raw_tool_calls = last_message.get("tool_calls", [])

        if raw_tool_calls:
            tool_calls_data = []
            for tool_call in raw_tool_calls:
                # Parse tool call structure from Swarm
                tool_call_dict = {
                    "id": tool_call.get("id", f"call_{int(time.time() * 1000)}"),
                    "name": tool_call.get("function", {}).get("name", "unknown"),
                    "arguments": json.loads(tool_call.get("function", {}).get("arguments", "{}")),
                    "result": None,  # Will be populated from tool execution
                }

                # Try to find the corresponding tool result in subsequent messages
                # Swarm returns tool results in separate messages
                for msg in response_messages:
                    if msg.get("role") == "tool" and msg.get("tool_call_id") == tool_call_dict["id"]:
                        try:
                            tool_call_dict["result"] = json.loads(msg.get("content", "{}"))
                        except json.JSONDecodeError:
                            tool_call_dict["result"] = {"raw": msg.get("content", "")}
                        break

                tool_calls_data.append(tool_call_dict)

        # Step 5: Save assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            tool_calls=tool_calls_data,
        )
        session.add(assistant_message)
        session.commit()
        session.refresh(assistant_message)

        # Step 6: Log tool invocations for audit
        if tool_calls_data:
            for tool_call in tool_calls_data:
                log_tool_invocation(
                    session=session,
                    message_id=assistant_message.id,
                    conversation_id=conversation.id,
                    user_id=current_user.id,
                    tool_call=tool_call,
                    execution_time_ms=execution_time_ms,
                )

        # Step 7: Auto-generate conversation title from first message if needed
        if not conversation.title:
            conversation.title = generate_conversation_title(request.message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # Step 8: Format response
        tool_calls = None
        if tool_calls_data:
            tool_calls = [
                ToolCallSchema(**call) for call in tool_calls_data
            ]

        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_content,
            tool_calls=tool_calls,
            created_at=assistant_message.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )
