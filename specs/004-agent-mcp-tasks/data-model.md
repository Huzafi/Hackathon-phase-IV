# Data Model: AI Agent & MCP Task Operations

**Feature**: 004-agent-mcp-tasks
**Date**: 2026-01-29
**Status**: Draft

## Overview

This feature extends the existing Todo application with AI agent capabilities. The data model includes new entities for conversation management and tool invocation tracking, while reusing existing User and Todo entities.

## Existing Entities (Phase I & II)

### User
**Purpose**: Represents an authenticated user account.

**Attributes**:
- `id` (int, PK): Unique user identifier
- `email` (string, unique, indexed): User email address
- `hashed_password` (string): Bcrypt-hashed password
- `created_at` (datetime): Account creation timestamp

**Relationships**:
- One-to-many with Todo (user owns multiple todos)
- One-to-many with Conversation (user has multiple conversations)

**Validation Rules**:
- Email must be valid format and unique
- Password must be hashed before storage
- Email is case-insensitive for uniqueness

### Todo
**Purpose**: Represents a task/todo item owned by a user.

**Attributes**:
- `id` (int, PK): Unique task identifier
- `title` (string, max 200): Task title
- `description` (string, max 1000, optional): Task description
- `is_completed` (boolean, default false): Completion status
- `user_id` (int, FK to User, indexed): Owner of the task
- `created_at` (datetime): Task creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Relationships**:
- Many-to-one with User (task belongs to one user)

**Validation Rules**:
- Title is required and non-empty
- User_id must reference existing user
- All queries must filter by user_id for data isolation

**Indexes**:
- Composite index on (user_id, created_at) for efficient user-scoped queries

## New Entities (Phase III)

### Conversation
**Purpose**: Represents a chat conversation between a user and the AI agent.

**Attributes**:
- `id` (string, PK): UUID for conversation identifier
- `user_id` (int, FK to User, indexed): Owner of the conversation
- `title` (string, max 200, optional): Conversation title (auto-generated from first message)
- `created_at` (datetime): Conversation start timestamp
- `updated_at` (datetime): Last message timestamp

**Relationships**:
- Many-to-one with User (conversation belongs to one user)
- One-to-many with Message (conversation contains multiple messages)

**Validation Rules**:
- User_id must reference existing user
- Title auto-generated from first user message if not provided
- All queries must filter by user_id for data isolation

**Indexes**:
- Index on user_id for listing user's conversations
- Index on (user_id, updated_at) for sorting by recent activity

**State Transitions**:
- Created → Active (when first message added)
- Active → Active (ongoing conversation)
- No explicit "closed" state (conversations remain accessible)

### Message
**Purpose**: Represents a single message in a conversation (user or assistant).

**Attributes**:
- `id` (int, PK): Unique message identifier
- `conversation_id` (string, FK to Conversation, indexed): Parent conversation
- `role` (enum: "user" | "assistant" | "system"): Message sender
- `content` (text): Message text content
- `tool_calls` (JSON, optional): Array of tool invocations (for assistant messages)
- `created_at` (datetime, indexed): Message timestamp

**Relationships**:
- Many-to-one with Conversation (message belongs to one conversation)
- One-to-many with ToolInvocation (message may trigger multiple tool calls)

**Validation Rules**:
- Conversation_id must reference existing conversation
- Role must be one of: "user", "assistant", "system"
- Content is required for user and assistant messages
- Tool_calls only valid for assistant messages
- Messages ordered by created_at within conversation

**Indexes**:
- Composite index on (conversation_id, created_at) for efficient message loading
- Index on created_at for chronological ordering

**JSON Schema for tool_calls**:
```json
[
  {
    "id": "call_abc123",
    "name": "create_task",
    "arguments": {
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    },
    "result": {
      "success": true,
      "message": "Task created successfully",
      "data": {
        "task_id": 123
      }
    }
  }
]
```

### ToolInvocation
**Purpose**: Audit log of all tool invocations for debugging and analytics.

**Attributes**:
- `id` (int, PK): Unique invocation identifier
- `message_id` (int, FK to Message, indexed): Message that triggered the tool
- `conversation_id` (string, FK to Conversation, indexed): Parent conversation
- `user_id` (int, FK to User, indexed): User who triggered the invocation
- `tool_name` (string): Name of the tool invoked (e.g., "create_task")
- `tool_arguments` (JSON): Input parameters passed to tool
- `tool_result` (JSON): Output returned by tool
- `success` (boolean): Whether tool execution succeeded
- `error_message` (string, optional): Error details if failed
- `execution_time_ms` (int): Tool execution duration in milliseconds
- `created_at` (datetime, indexed): Invocation timestamp

**Relationships**:
- Many-to-one with Message (invocation triggered by one message)
- Many-to-one with Conversation (invocation part of one conversation)
- Many-to-one with User (invocation performed for one user)

**Validation Rules**:
- All foreign keys must reference existing records
- Tool_name must be one of: "create_task", "list_tasks", "update_task", "delete_task"
- Tool_arguments and tool_result must be valid JSON
- Success must be boolean
- Execution_time_ms must be non-negative

**Indexes**:
- Index on user_id for user-specific analytics
- Index on (tool_name, created_at) for tool usage analytics
- Index on conversation_id for conversation-level debugging

**Use Cases**:
- Debugging tool failures
- Analytics on tool usage patterns
- Performance monitoring
- Audit trail for compliance

## Entity Relationships Diagram

```
User (existing)
  ├─── todos (1:N) ──→ Todo (existing)
  ├─── conversations (1:N) ──→ Conversation (new)
  └─── tool_invocations (1:N) ──→ ToolInvocation (new)

Conversation (new)
  ├─── messages (1:N) ──→ Message (new)
  └─── tool_invocations (1:N) ──→ ToolInvocation (new)

Message (new)
  └─── tool_invocations (1:N) ──→ ToolInvocation (new)
```

## Data Access Patterns

### User-Scoped Queries (Security Critical)
All queries MUST filter by user_id to enforce data isolation:

```sql
-- List user's conversations
SELECT * FROM conversations
WHERE user_id = ?
ORDER BY updated_at DESC;

-- Load conversation messages
SELECT m.* FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.user_id = ? AND m.conversation_id = ?
ORDER BY m.created_at ASC;

-- List user's tasks (existing)
SELECT * FROM todos
WHERE user_id = ?
ORDER BY created_at DESC;

-- Get tool invocation history
SELECT * FROM tool_invocations
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 100;
```

### Context Window Loading
Load last N messages for agent context:

```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 20;
```

### Tool Invocation Logging
Insert tool invocation record after each tool call:

```sql
INSERT INTO tool_invocations (
  message_id, conversation_id, user_id,
  tool_name, tool_arguments, tool_result,
  success, execution_time_ms, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
```

## Migration Strategy

### Phase 1: Add New Tables
1. Create `conversations` table
2. Create `messages` table
3. Create `tool_invocations` table
4. Add foreign key constraints
5. Create indexes

### Phase 2: Seed Data (Optional)
- No seed data required
- Conversations created on-demand when users start chatting

### Phase 3: Validation
- Verify foreign key constraints
- Test user-scoped queries
- Validate JSON schema for tool_calls and tool_result

## Storage Estimates

### Assumptions
- 1000 active users
- Average 10 conversations per user
- Average 50 messages per conversation
- Average 2 tool invocations per assistant message

### Calculations
- Conversations: 1000 users × 10 = 10,000 rows (~1 MB)
- Messages: 10,000 conversations × 50 = 500,000 rows (~100 MB)
- Tool Invocations: 500,000 messages × 0.5 (assistant only) × 2 = 500,000 rows (~150 MB)

**Total**: ~250 MB for 1000 active users

### Retention Policy
- Keep all conversations indefinitely (user data)
- Archive tool_invocations older than 90 days (analytics only)
- No automatic deletion of messages (user expects persistence)

## Performance Considerations

### Indexes
All critical indexes defined above for:
- User-scoped queries (user_id)
- Conversation loading (conversation_id, created_at)
- Message ordering (created_at)
- Tool analytics (tool_name, created_at)

### Query Optimization
- Limit context window to 20 messages (configurable)
- Use pagination for conversation lists
- Batch insert for tool invocations
- Connection pooling for concurrent requests

### Scaling Strategy
- Partition messages table by conversation_id (future)
- Read replicas for analytics queries (future)
- Archive old tool_invocations to separate table (future)

## Security Considerations

### Data Isolation
- All queries MUST include user_id filter
- Foreign key constraints prevent orphaned records
- No cross-user data access possible

### Sensitive Data
- Message content may contain PII (user's tasks)
- Tool arguments may contain sensitive data
- Encrypt at rest (database level)
- Encrypt in transit (TLS)

### Audit Trail
- Tool invocations provide complete audit log
- All actions traceable to user_id and timestamp
- Immutable log (no updates, only inserts)
