# Research: AI Agent & MCP Task Operations

**Feature**: 004-agent-mcp-tasks
**Date**: 2026-01-29
**Status**: Complete

## 1. OpenAI Agents SDK Integration

### Decision
Use OpenAI Agents SDK (Swarm framework) for agent orchestration with custom MCP tools.

### Rationale
- **Native tool support**: Swarm provides built-in tool calling with function definitions
- **Stateless by design**: Each agent invocation is independent, aligning with our architecture
- **Simple integration**: Works seamlessly with OpenAI API and custom tool functions
- **Type safety**: Tool schemas defined with Python type hints
- **Error handling**: Built-in error propagation from tool failures to agent responses

### Alternatives Considered
- **LangChain Agents**: More complex, heavier dependencies, overkill for our use case
- **Custom agent loop**: Would require reimplementing tool calling logic, error handling, and response formatting
- **AutoGPT/BabyAGI**: Too autonomous, we need deterministic tool execution

### Implementation Guidance
```python
# Agent initialization pattern
from swarm import Swarm, Agent

client = Swarm()

agent = Agent(
    name="TodoAgent",
    instructions="""You are a helpful assistant that manages todos.
    You can create, list, update, and delete tasks using the provided tools.
    Always confirm actions and provide clear feedback.""",
    functions=[create_task, list_tasks, update_task, delete_task]
)

# Tool invocation pattern
response = client.run(
    agent=agent,
    messages=conversation_history,
    context_variables={"user_id": user_id}
)
```

**Key patterns**:
- Agent instructions define behavior and tone
- Tools are Python functions with type hints
- Context variables pass user_id to all tools
- Response includes messages and tool calls

## 2. MCP (Model Context Protocol) SDK

### Decision
Implement MCP tools as Python functions following MCP protocol standards, integrated with FastAPI backend.

### Rationale
- **Stateless design**: Each tool receives all context (user_id, parameters) in function call
- **Schema validation**: Pydantic models enforce input/output types
- **Database integration**: Tools use existing SQLModel session for data access
- **Error handling**: Tools return structured error responses
- **Auditability**: All tool calls logged with user context

### Alternatives Considered
- **Separate MCP server**: Adds network latency and deployment complexity
- **Direct database access from agent**: Violates stateless architecture principle
- **REST API calls from agent**: Unnecessary overhead when tools can be Python functions

### Implementation Guidance
```python
# MCP tool definition pattern
from pydantic import BaseModel, Field
from typing import Optional

class CreateTaskInput(BaseModel):
    """Input schema for create_task tool."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")

class CreateTaskOutput(BaseModel):
    """Output schema for create_task tool."""
    success: bool
    task_id: Optional[int] = None
    message: str
    error: Optional[str] = None

def create_task(
    title: str,
    description: Optional[str] = None,
    user_id: int = None  # Injected from context
) -> dict:
    """Create a new task for the authenticated user.

    Args:
        title: Task title
        description: Optional task description
        user_id: Authenticated user ID (from context)

    Returns:
        CreateTaskOutput dict with success status and task details
    """
    try:
        # Validate user_id
        if not user_id:
            return {
                "success": False,
                "message": "Authentication required",
                "error": "USER_NOT_AUTHENTICATED"
            }

        # Create task in database
        with get_session() as session:
            task = Todo(
                title=title,
                description=description,
                user_id=user_id
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task_id": task.id,
                "message": f"Created task: {title}"
            }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {
            "success": False,
            "message": "Failed to create task",
            "error": str(e)
        }
```

**Key patterns**:
- Tools are pure functions with explicit parameters
- User context injected via context_variables
- Structured error responses with error codes
- Database operations in try/except blocks
- All operations user-scoped (WHERE user_id = ?)

## 3. Stateless Chat Architecture

### Decision
Rebuild conversation context from database on every chat request, no in-memory state.

### Rationale
- **Horizontal scaling**: Any server can handle any request
- **Crash recovery**: No state lost on restart
- **Multi-device support**: Users can switch devices seamlessly
- **Auditability**: Complete conversation history in database
- **Simplicity**: No cache invalidation or state synchronization

### Alternatives Considered
- **In-memory cache**: Faster but violates stateless principle, complicates deployment
- **Redis session store**: Adds dependency, still requires database for persistence
- **Sticky sessions**: Limits scaling, single point of failure

### Implementation Guidance
```python
# Chat endpoint pattern
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Handle chat message and return agent response."""

    # 1. Load or create conversation
    conversation = get_or_create_conversation(
        session=session,
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )

    # 2. Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    session.commit()

    # 3. Load conversation history (last N messages)
    messages = load_conversation_history(
        session=session,
        conversation_id=conversation.id,
        limit=20  # Context window limit
    )

    # 4. Invoke agent with full context
    response = client.run(
        agent=todo_agent,
        messages=messages,
        context_variables={"user_id": current_user.id}
    )

    # 5. Save agent response and tool calls
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response.messages[-1]["content"],
        tool_calls=response.messages[-1].get("tool_calls"),
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)
    session.commit()

    # 6. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        message=assistant_message.content,
        tool_calls=assistant_message.tool_calls
    )
```

**Performance considerations**:
- Limit context window to last 20 messages (configurable)
- Index conversation_id and created_at for fast queries
- Use database connection pooling
- Consider read replicas for high load

## 4. Tool Schema Design

### Decision
Define tools with explicit schemas using Pydantic models, following OpenAI function calling format.

### Rationale
- **Type safety**: Pydantic validates inputs at runtime
- **Documentation**: Schemas serve as API documentation
- **Error prevention**: Invalid inputs rejected before execution
- **IDE support**: Type hints enable autocomplete and linting

### Tool Definitions

#### create_task
```python
{
    "name": "create_task",
    "description": "Create a new task for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title (required)"
            },
            "description": {
                "type": "string",
                "description": "Optional task description"
            }
        },
        "required": ["title"]
    }
}
```

#### list_tasks
```python
{
    "name": "list_tasks",
    "description": "List all tasks for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "completed": {
                "type": "boolean",
                "description": "Filter by completion status (optional)"
            }
        }
    }
}
```

#### update_task
```python
{
    "name": "update_task",
    "description": "Update an existing task",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of task to update"
            },
            "title": {
                "type": "string",
                "description": "New task title (optional)"
            },
            "description": {
                "type": "string",
                "description": "New task description (optional)"
            },
            "is_completed": {
                "type": "boolean",
                "description": "Completion status (optional)"
            }
        },
        "required": ["task_id"]
    }
}
```

#### delete_task
```python
{
    "name": "delete_task",
    "description": "Delete a task",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of task to delete"
            }
        },
        "required": ["task_id"]
    }
}
```

## 5. Agent-to-Frontend Integration

### Decision
Return structured responses with message content and tool call metadata for UI consumption.

### Rationale
- **Transparency**: Users see what actions the agent took
- **Debugging**: Tool calls visible in UI for troubleshooting
- **User control**: Users can confirm or reject actions
- **Rich UI**: Frontend can render tool calls as structured components

### Response Format
```typescript
interface ChatResponse {
  conversation_id: string;
  message: string;  // Natural language response
  tool_calls?: ToolCall[];  // Optional tool invocations
  created_at: string;
}

interface ToolCall {
  id: string;
  name: string;  // e.g., "create_task"
  arguments: Record<string, any>;  // e.g., {"title": "Buy groceries"}
  result?: {
    success: boolean;
    message: string;
    data?: any;
  };
}
```

### Frontend Integration Pattern
```typescript
// ChatKit integration
const handleSendMessage = async (message: string) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message: message
    })
  });

  const data = await response.json();

  // Display agent message
  addMessage({
    role: 'assistant',
    content: data.message,
    tool_calls: data.tool_calls
  });

  // Optionally render tool calls as badges/chips
  if (data.tool_calls) {
    renderToolCalls(data.tool_calls);
  }
};
```

## 6. Error Handling Patterns

### Tool Error Responses
```python
# Success response
{
    "success": True,
    "message": "Task created successfully",
    "data": {"task_id": 123, "title": "Buy groceries"}
}

# Validation error
{
    "success": False,
    "message": "Invalid task ID",
    "error": "TASK_NOT_FOUND"
}

# Permission error
{
    "success": False,
    "message": "You don't have permission to access this task",
    "error": "PERMISSION_DENIED"
}

# Database error
{
    "success": False,
    "message": "Failed to create task. Please try again.",
    "error": "DATABASE_ERROR"
}
```

### Agent Error Handling
- Agent receives tool error responses and translates to user-friendly messages
- Example: "I couldn't create that task. Please try again." instead of "DATABASE_ERROR"
- Errors logged with full context for debugging

## 7. Security Considerations

### User Context Enforcement
- **Every tool call** receives user_id from JWT token
- **All database queries** filter by user_id
- **No cross-user access** possible through tools
- **Tool invocation logging** includes user_id for audit trail

### Input Validation
- Pydantic models validate all tool inputs
- SQL injection prevented by SQLModel parameterized queries
- XSS prevention by sanitizing user inputs
- Rate limiting on chat endpoint (future enhancement)

## 8. Performance Optimization

### Database Queries
- Index on (conversation_id, created_at) for message loading
- Index on (user_id, created_at) for task queries
- Connection pooling for concurrent requests
- Limit context window to prevent large queries

### Agent Invocation
- Async/await for non-blocking I/O
- Timeout on agent calls (30 seconds max)
- Retry logic for transient failures
- Caching of agent configuration (not conversation state)

## Summary

This architecture provides:
- ✅ Stateless, horizontally scalable design
- ✅ Deterministic tool execution with full auditability
- ✅ Type-safe tool definitions with validation
- ✅ User-scoped data access enforced at tool level
- ✅ Clear error handling and user feedback
- ✅ Frontend-friendly response format
- ✅ Production-ready security and performance patterns
