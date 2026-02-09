---
id: 0004
title: Create SQLModel database models for AI agent
stage: red
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-agent-mcp-tasks
branch: 004-agent-mcp-tasks
user: STAR
command: direct-request
labels: ["database", "sqlmodel", "models", "schema", "relationships"]
links:
  spec: specs/004-agent-mcp-tasks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/models/conversation.py
  - backend/src/models/message.py
  - backend/src/models/tool_invocation.py
  - backend/src/models/user.py
  - backend/src/models/__init__.py
  - backend/src/core/database.py
tests:
  - Model import verification test
  - Schema structure verification test
  - Relationship verification test
  - Foreign key constraint verification test
  - Index verification test
---

## Prompt

Create the following SQLModel database models for the AI agent chat feature:

**Context**: This is Phase III of a todo application. We're adding AI agent capabilities with conversation management. Existing models: User (id, email, hashed_password, created_at) and Todo (id, title, description, is_completed, user_id, created_at, updated_at).

**Task**: Create three new models in backend/src/models/:

1. **Conversation model** (backend/src/models/conversation.py):
   - id: UUID (primary key)
   - user_id: int (foreign key to User, indexed)
   - title: Optional[str] (max 200 chars)
   - created_at: datetime
   - updated_at: datetime
   - Relationships: belongs to User, has many Messages
   - Indexes: user_id, (user_id, updated_at)

2. **Message model** (backend/src/models/message.py):
   - id: int (primary key)
   - conversation_id: str (foreign key to Conversation, indexed)
   - role: Literal["user", "assistant", "system"]
   - content: str (text field)
   - tool_calls: Optional[dict] (JSON field)
   - created_at: datetime (indexed)
   - Relationships: belongs to Conversation
   - Indexes: (conversation_id, created_at), created_at

3. **ToolInvocation model** (backend/src/models/tool_invocation.py):
   - id: int (primary key)
   - message_id: int (foreign key to Message, indexed)
   - conversation_id: str (foreign key to Conversation, indexed)
   - user_id: int (foreign key to User, indexed)
   - tool_name: str
   - tool_arguments: dict (JSON field)
   - tool_result: dict (JSON field)
   - success: bool
   - error_message: Optional[str]
   - execution_time_ms: int
   - created_at: datetime (indexed)
   - Relationships: belongs to Message, Conversation, User
   - Indexes: user_id, (tool_name, created_at), conversation_id

4. **Update database initialization** in backend/src/core/database.py:
   - Import the new models
   - Add them to create_db_and_tables() function

**Requirements**:
- Use SQLModel for all models
- Follow existing code patterns from User and Todo models
- Add proper type hints and validation
- Include docstrings for each model
- Ensure all foreign keys are properly defined
- Create indexes as specified above

**Reference**: See specs/004-agent-mcp-tasks/data-model.md for complete schema details.

## Response snapshot

Successfully created three new SQLModel database models for the AI agent chat feature:

**1. Conversation Model** (G:\Hackathon-2\phase-II\backend\src\models\conversation.py):
- UUID primary key with auto-generation using uuid4()
- Foreign key to User with index
- Optional title field (max 200 chars)
- Timestamps for created_at and updated_at
- Relationships: belongs to User, has many Messages and ToolInvocations
- Composite index on (user_id, updated_at) for efficient recent conversation queries

**2. Message Model** (G:\Hackathon-2\phase-II\backend\src\models\message.py):
- Integer primary key
- Foreign key to Conversation
- Role field using MessageRole Enum (user, assistant, system) - changed from Literal to Enum for SQLModel compatibility
- Text content field using SQLAlchemy Text type
- Optional JSON tool_calls field
- Indexed created_at timestamp
- Relationships: belongs to Conversation, has many ToolInvocations
- Composite index on (conversation_id, created_at) for efficient message loading

**3. ToolInvocation Model** (G:\Hackathon-2\phase-II\backend\src\models\tool_invocation.py):
- Integer primary key
- Foreign keys to Message, Conversation, and User (all indexed)
- Tool metadata: name, arguments (JSON), result (JSON)
- Execution tracking: success flag, error_message, execution_time_ms
- Indexed created_at timestamp
- Relationships: belongs to Message, Conversation, and User
- Composite index on (tool_name, created_at) for analytics

**4. Updated User Model** (G:\Hackathon-2\phase-II\backend\src\models\user.py):
- Added relationships to Conversation and ToolInvocation
- Maintains existing Todo relationship

**5. Updated Database Initialization** (G:\Hackathon-2\phase-II\backend\src\core\database.py):
- Imported all new models to register with SQLModel metadata
- Enhanced docstring for create_db_and_tables() to document all tables

**6. Updated Models Package** (G:\Hackathon-2\phase-II\backend\src\models\__init__.py):
- Exported all models including MessageRole enum
- Clean __all__ declaration for explicit exports

**Key Implementation Details**:
- Used Python Enum instead of Literal for MessageRole (SQLModel compatibility)
- Used SQLAlchemy Column with JSON type for JSON fields
- Used SQLAlchemy Text type for message content (unbounded text)
- UUID generation using uuid4() with string conversion for database storage
- All foreign keys properly defined with nullable=False
- All indexes created as specified in the data model spec
- Followed existing code patterns from User and Todo models
- Added comprehensive docstrings for each model

**Verification Results**:
- All models import successfully without errors
- Schema verification shows 5 tables registered: users, todos, conversations, messages, tool_invocations
- All foreign key constraints properly defined (7 total)
- All indexes created as specified (13 total across all tables)
- Relationships properly configured with TYPE_CHECKING guards to avoid circular imports

## Outcome

- ✅ Impact: Created complete database schema for AI agent chat feature with 3 new models, proper relationships, and all required indexes
- 🧪 Tests: Model import test, schema structure test, relationship verification, foreign key verification, index verification - all passed
- 📁 Files: 6 files created/modified (3 new models, 3 updated files)
- 🔁 Next prompts: Create Pydantic schemas for API request/response validation, implement API routers for conversation and message endpoints
- 🧠 Reflection: Initial attempt used Literal type for MessageRole which caused SQLModel compatibility issue; resolved by using Python Enum. All models follow existing patterns and include proper type hints, docstrings, and database constraints.

## Evaluation notes (flywheel)

- Failure modes observed: SQLModel doesn't support Literal types directly - must use Python Enum for database enum fields
- Graders run and results (PASS/FAIL): Model import test (PASS), Schema verification (PASS), Relationship verification (PASS), Foreign key verification (PASS), Index verification (PASS)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test database table creation with actual Neon PostgreSQL connection to verify schema migrations work correctly
