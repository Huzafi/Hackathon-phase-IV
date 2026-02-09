# MCP Tools Schema

**Feature**: 004-agent-mcp-tasks
**Date**: 2026-01-29
**Protocol**: Model Context Protocol (MCP)

## Overview

This document defines the MCP tools that the AI agent uses to perform task operations. All tools are stateless, receive user context as parameters, and return structured responses.

## Tool Definitions

### 1. create_task

**Purpose**: Create a new task for the authenticated user.

**Schema**:
```json
{
  "name": "create_task",
  "description": "Create a new task for the user. Use this when the user wants to add a todo item.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required). Extract from user's message.",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Optional task description with additional details.",
        "maxLength": 1000
      }
    },
    "required": ["title"]
  }
}
```

**Input Example**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the operation succeeded"
    },
    "message": {
      "type": "string",
      "description": "Human-readable result message"
    },
    "data": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "ID of the created task"
        },
        "title": {
          "type": "string",
          "description": "Task title"
        },
        "is_completed": {
          "type": "boolean",
          "description": "Completion status (always false for new tasks)"
        }
      }
    },
    "error": {
      "type": "string",
      "description": "Error code if operation failed"
    }
  },
  "required": ["success", "message"]
}
```

**Output Examples**:

Success:
```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "task_id": 123,
    "title": "Buy groceries",
    "is_completed": false
  }
}
```

Failure:
```json
{
  "success": false,
  "message": "Failed to create task",
  "error": "DATABASE_ERROR"
}
```

---

### 2. list_tasks

**Purpose**: Retrieve all tasks for the authenticated user.

**Schema**:
```json
{
  "name": "list_tasks",
  "description": "List all tasks for the user. Use this when the user asks to see their todos.",
  "parameters": {
    "type": "object",
    "properties": {
      "completed": {
        "type": "boolean",
        "description": "Filter by completion status. If null, return all tasks.",
        "nullable": true
      }
    }
  }
}
```

**Input Examples**:
```json
{}  // List all tasks
```
```json
{"completed": false}  // List only incomplete tasks
```
```json
{"completed": true}  // List only completed tasks
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "object",
      "properties": {
        "tasks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "integer"},
              "title": {"type": "string"},
              "description": {"type": "string", "nullable": true},
              "is_completed": {"type": "boolean"},
              "created_at": {"type": "string", "format": "date-time"},
              "updated_at": {"type": "string", "format": "date-time"}
            }
          }
        },
        "total": {
          "type": "integer",
          "description": "Total number of tasks returned"
        }
      }
    },
    "error": {
      "type": "string"
    }
  },
  "required": ["success", "message"]
}
```

**Output Examples**:

Success with tasks:
```json
{
  "success": true,
  "message": "Retrieved 3 tasks",
  "data": {
    "tasks": [
      {
        "id": 123,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "is_completed": false,
        "created_at": "2026-01-29T10:00:00Z",
        "updated_at": "2026-01-29T10:00:00Z"
      },
      {
        "id": 124,
        "title": "Finish report",
        "description": null,
        "is_completed": false,
        "created_at": "2026-01-29T09:00:00Z",
        "updated_at": "2026-01-29T09:00:00Z"
      },
      {
        "id": 125,
        "title": "Call mom",
        "description": null,
        "is_completed": true,
        "created_at": "2026-01-28T15:00:00Z",
        "updated_at": "2026-01-29T08:00:00Z"
      }
    ],
    "total": 3
  }
}
```

Success with no tasks:
```json
{
  "success": true,
  "message": "No tasks found",
  "data": {
    "tasks": [],
    "total": 0
  }
}
```

---

### 3. update_task

**Purpose**: Update an existing task's properties.

**Schema**:
```json
{
  "name": "update_task",
  "description": "Update an existing task. Use this when the user wants to modify a task or mark it as complete.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of the task to update (required)"
      },
      "title": {
        "type": "string",
        "description": "New task title (optional)",
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "New task description (optional)",
        "maxLength": 1000
      },
      "is_completed": {
        "type": "boolean",
        "description": "New completion status (optional)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Input Examples**:
```json
{
  "task_id": 123,
  "is_completed": true
}
```
```json
{
  "task_id": 124,
  "title": "Finish quarterly report",
  "description": "Due by end of month"
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "message": {"type": "string"},
    "data": {
      "type": "object",
      "properties": {
        "task_id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string", "nullable": true},
        "is_completed": {"type": "boolean"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "error": {"type": "string"}
  },
  "required": ["success", "message"]
}
```

**Output Examples**:

Success:
```json
{
  "success": true,
  "message": "Task updated successfully",
  "data": {
    "task_id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": true,
    "updated_at": "2026-01-29T11:00:00Z"
  }
}
```

Task not found:
```json
{
  "success": false,
  "message": "Task not found or you don't have permission",
  "error": "TASK_NOT_FOUND"
}
```

---

### 4. delete_task

**Purpose**: Delete a task permanently.

**Schema**:
```json
{
  "name": "delete_task",
  "description": "Delete a task permanently. Use this when the user wants to remove a task.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of the task to delete (required)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Input Example**:
```json
{
  "task_id": 123
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "message": {"type": "string"},
    "data": {
      "type": "object",
      "properties": {
        "task_id": {"type": "integer"},
        "title": {"type": "string"}
      }
    },
    "error": {"type": "string"}
  },
  "required": ["success", "message"]
}
```

**Output Examples**:

Success:
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "data": {
    "task_id": 123,
    "title": "Buy groceries"
  }
}
```

Task not found:
```json
{
  "success": false,
  "message": "Task not found or you don't have permission",
  "error": "TASK_NOT_FOUND"
}
```

---

## Error Codes

All tools use standardized error codes:

| Error Code | Description | HTTP Equivalent |
|------------|-------------|-----------------|
| `USER_NOT_AUTHENTICATED` | User context missing or invalid | 401 |
| `TASK_NOT_FOUND` | Task doesn't exist or user lacks permission | 404 |
| `VALIDATION_ERROR` | Invalid input parameters | 422 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `UNKNOWN_ERROR` | Unexpected error occurred | 500 |

## User Context Injection

All tools receive user context via the `context_variables` parameter in Swarm:

```python
response = client.run(
    agent=agent,
    messages=messages,
    context_variables={"user_id": current_user.id}
)
```

Tools access user_id from context:
```python
def create_task(title: str, description: str = None, context_variables: dict = None):
    user_id = context_variables.get("user_id")
    if not user_id:
        return {"success": False, "error": "USER_NOT_AUTHENTICATED"}
    # ... rest of implementation
```

## Security Enforcement

Every tool MUST:
1. Validate user_id from context_variables
2. Filter all database queries by user_id
3. Return permission error if user_id missing
4. Log all invocations with user_id for audit

Example query pattern:
```python
# CORRECT: User-scoped query
task = session.exec(
    select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)
).first()

# WRONG: No user filtering (security vulnerability)
task = session.exec(select(Todo).where(Todo.id == task_id)).first()
```

## Performance Guidelines

- Tool execution MUST complete within 5 seconds
- Database queries MUST use indexes (user_id, created_at)
- Batch operations not supported (one task per call)
- No caching (stateless design)

## Testing Strategy

Each tool requires:
1. **Unit tests**: Test tool function in isolation with mocked database
2. **Integration tests**: Test tool with real database and user context
3. **Security tests**: Verify user isolation (cross-user access blocked)
4. **Error tests**: Verify all error codes returned correctly

Example test cases:
- Create task with valid input → success
- Create task without user_id → USER_NOT_AUTHENTICATED
- Update task belonging to another user → TASK_NOT_FOUND
- Delete non-existent task → TASK_NOT_FOUND
- List tasks with database error → DATABASE_ERROR
