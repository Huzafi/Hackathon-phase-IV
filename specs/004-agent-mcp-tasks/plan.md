# Implementation Plan: AI Agent & MCP Task Operations

**Branch**: `004-agent-mcp-tasks` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-agent-mcp-tasks/spec.md`

## Summary

This feature adds AI agent capabilities to the Todo application, enabling users to manage tasks through natural language chat. The agent uses OpenAI Agents SDK (Swarm) to interpret user intent and invokes stateless MCP tools for CRUD operations on tasks. All conversations are persisted in the database, and context is rebuilt on every request to maintain a stateless architecture.

**Primary Requirement**: Enable natural language task management through an AI agent that uses MCP tools exclusively for all operations.

**Technical Approach**:
- OpenAI Agents SDK (Swarm) for agent orchestration
- MCP tools as Python functions with Pydantic schemas
- Stateless chat endpoint that rebuilds context from database
- New database entities: Conversation, Message, ToolInvocation
- FastAPI endpoints for chat and conversation management

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastAPI (latest) - Web framework
- SQLModel (latest) - ORM for database operations
- OpenAI Agents SDK (Swarm) - Agent orchestration
- Pydantic v2 - Schema validation
- OpenAI Python SDK - LLM API client

**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: pytest with fixtures for database and agent mocking
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend + frontend)
**Performance Goals**:
- Chat response time < 5 seconds (including tool execution)
- Tool execution < 2 seconds per operation
- Support 100 concurrent chat sessions

**Constraints**:
- Stateless architecture (no in-memory state between requests)
- All tool calls must be user-scoped (security critical)
- Context window limited to 20 messages (performance)
- Agent must use MCP tools only (no direct database access)

**Scale/Scope**:
- 1000 active users
- Average 10 conversations per user
- Average 50 messages per conversation
- 4 MCP tools (create, list, update, delete)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development (SDD)
- **Status**: PASS
- **Evidence**: Feature has complete spec.md with user stories, requirements, and success criteria
- **Compliance**: Following SDD workflow (spec → plan → tasks → implement)

### ✅ II. Security-First Design
- **Status**: PASS
- **Evidence**:
  - Chat endpoint requires JWT authentication
  - All MCP tools enforce user_id filtering
  - All database queries include WHERE user_id = ?
  - Tool invocation logging includes user_id for audit
- **Compliance**: User isolation enforced at tool level, no cross-user access possible

### ✅ III. Zero Manual Coding
- **Status**: PASS
- **Evidence**: All code will be generated via Claude Code with specialized agents
- **Compliance**: Using fastapi-backend-dev agent for backend, neon-db-specialist for database

### ✅ IV. Clear Separation of Concerns
- **Status**: PASS
- **Evidence**:
  - Frontend: Next.js App Router (consumes chat API)
  - Backend: FastAPI (stateless endpoints)
  - Database: Neon PostgreSQL (via SQLModel)
  - AI Agent: OpenAI Agents SDK (uses MCP tools only)
  - MCP Tools: Python functions (stateless, schema-driven)
- **Compliance**: Agent cannot access database directly, must use tools

### ✅ V. Multi-User Data Isolation
- **Status**: PASS
- **Evidence**:
  - All conversations filtered by user_id
  - All messages belong to user's conversations
  - All tool invocations include user_id
  - Tools validate user ownership before operations
- **Compliance**: Every database query includes user_id filter

### ✅ VI. Environment-Based Configuration
- **Status**: PASS
- **Evidence**:
  - OpenAI API key in .env (OPENAI_API_KEY)
  - Database connection string in .env (existing)
  - JWT secret in .env (existing)
- **Compliance**: No secrets hardcoded, all externalized

### ✅ VII. Stateless Architecture with Persistent State
- **Status**: PASS
- **Evidence**:
  - Chat endpoint loads conversation history from database on every request
  - No in-memory session state
  - Agent invoked fresh each time with full context
  - Conversations and messages persisted in database
- **Compliance**: Application can restart without losing state

### ✅ VIII. AI Agents via MCP Tools Only
- **Status**: PASS
- **Evidence**:
  - Agent receives tools as function definitions
  - Tools are Python functions with explicit schemas
  - Agent cannot access database, filesystem, or external APIs
  - All actions expressed as tool invocations
- **Compliance**: Agent behavior deterministic and auditable through tool logs

### ✅ IX. Conversation Persistence and Context Rebuilding
- **Status**: PASS
- **Evidence**:
  - Conversation entity stores chat sessions
  - Message entity stores all user/assistant messages
  - Chat endpoint loads last 20 messages for context
  - Tool calls stored in message.tool_calls JSON field
- **Compliance**: Users can resume conversations after logout/restart

**Overall Status**: ✅ ALL GATES PASS - Ready to proceed with implementation

## Project Structure

### Documentation (this feature)

```text
specs/004-agent-mcp-tasks/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Technical research (complete)
├── data-model.md        # Database schema (complete)
├── quickstart.md        # Developer guide (to be created)
├── contracts/
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints (complete)
│   └── mcp-tools.md     # MCP tool schemas (complete)
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agent/                    # NEW: AI agent module
│   │   ├── __init__.py
│   │   ├── agent.py              # Agent initialization and configuration
│   │   ├── tools.py              # MCP tool implementations
│   │   └── prompts.py            # Agent system prompts
│   ├── api/
│   │   ├── auth.py               # Existing: Authentication endpoints
│   │   ├── todos.py              # Existing: Todo CRUD endpoints
│   │   ├── chat.py               # NEW: Chat endpoint
│   │   └── conversations.py     # NEW: Conversation management endpoints
│   ├── models/
│   │   ├── user.py               # Existing: User model
│   │   ├── todo.py               # Existing: Todo model
│   │   ├── conversation.py      # NEW: Conversation model
│   │   ├── message.py           # NEW: Message model
│   │   └── tool_invocation.py  # NEW: ToolInvocation model
│   ├── schemas/
│   │   ├── auth.py               # Existing: Auth schemas
│   │   ├── todo.py               # Existing: Todo schemas
│   │   ├── chat.py               # NEW: Chat request/response schemas
│   │   └── conversation.py      # NEW: Conversation schemas
│   ├── core/
│   │   ├── config.py             # Existing: Configuration (add OPENAI_API_KEY)
│   │   ├── database.py           # Existing: Database connection
│   │   └── security.py           # Existing: JWT utilities
│   ├── dependencies/
│   │   └── auth.py               # Existing: Auth dependencies
│   └── main.py                   # Existing: FastAPI app (register new routers)
└── tests/
    ├── test_agent/               # NEW: Agent tests
    │   ├── test_tools.py         # Tool unit tests
    │   └── test_agent.py         # Agent integration tests
    ├── test_api/
    │   ├── test_chat.py          # NEW: Chat endpoint tests
    │   └── test_conversations.py # NEW: Conversation endpoint tests
    └── conftest.py               # Existing: Test fixtures (add agent fixtures)

frontend/
├── app/
│   └── (protected)/
│       └── chat/                 # NEW: Chat page (future - not in this feature)
└── components/
    └── chat/                     # NEW: Chat components (future - not in this feature)
```

**Structure Decision**: Web application structure with backend/frontend separation. This feature focuses on backend implementation (agent + MCP tools + chat API). Frontend integration is out of scope per spec.md.

## Complexity Tracking

> **No violations detected** - All constitutional principles satisfied without exceptions.

## Implementation Phases

### Phase 0: Research ✅ COMPLETE

**Status**: Research completed in research.md

**Key Decisions**:
1. OpenAI Agents SDK (Swarm) for agent orchestration
2. MCP tools as Python functions with Pydantic schemas
3. Stateless chat endpoint with database context loading
4. Tool invocation logging for audit trail

### Phase 1: Database Schema & Models

**Objective**: Add new database entities for conversation management

**Tasks**:
1. Create Conversation model (SQLModel)
   - Fields: id (UUID), user_id (FK), title, created_at, updated_at
   - Relationships: belongs to User, has many Messages
   - Indexes: user_id, (user_id, updated_at)

2. Create Message model (SQLModel)
   - Fields: id, conversation_id (FK), role (enum), content, tool_calls (JSON), created_at
   - Relationships: belongs to Conversation
   - Indexes: (conversation_id, created_at), created_at

3. Create ToolInvocation model (SQLModel)
   - Fields: id, message_id (FK), conversation_id (FK), user_id (FK), tool_name, tool_arguments (JSON), tool_result (JSON), success, error_message, execution_time_ms, created_at
   - Relationships: belongs to Message, Conversation, User
   - Indexes: user_id, (tool_name, created_at), conversation_id

4. Create database migration
   - Add new tables with foreign key constraints
   - Create indexes for performance
   - Test migration rollback

5. Update database initialization
   - Modify create_db_and_tables() to include new models
   - Verify foreign key constraints

**Acceptance Criteria**:
- All models defined with proper types and relationships
- Database migration creates tables successfully
- Indexes created for all foreign keys and query patterns
- User-scoped queries tested and verified

### Phase 2: MCP Tools Implementation

**Objective**: Implement stateless MCP tools for task operations

**Tasks**:
1. Create tools module (backend/src/agent/tools.py)
   - Define tool function signatures with type hints
   - Implement user context injection pattern
   - Add input validation with Pydantic

2. Implement create_task tool
   - Accept title, description, user_id (from context)
   - Create Todo record in database
   - Return structured response with task_id
   - Handle database errors gracefully

3. Implement list_tasks tool
   - Accept optional completed filter, user_id (from context)
   - Query todos filtered by user_id
   - Return array of tasks with metadata
   - Handle empty results

4. Implement update_task tool
   - Accept task_id, optional title/description/is_completed, user_id (from context)
   - Verify task ownership (user_id match)
   - Update task fields
   - Return updated task data
   - Handle task not found / permission denied

5. Implement delete_task tool
   - Accept task_id, user_id (from context)
   - Verify task ownership
   - Delete task from database
   - Return confirmation
   - Handle task not found / permission denied

6. Add tool invocation logging
   - Create log_tool_invocation() helper
   - Log all tool calls to ToolInvocation table
   - Include user_id, tool_name, arguments, result, execution_time
   - Handle logging failures gracefully (don't block tool execution)

**Acceptance Criteria**:
- All 4 tools implemented with proper schemas
- User context enforced in every tool
- All database queries filter by user_id
- Structured error responses for all failure cases
- Tool invocations logged to database
- Unit tests for each tool with mocked database

### Phase 3: AI Agent Configuration

**Objective**: Configure OpenAI agent with MCP tools

**Tasks**:
1. Create agent module (backend/src/agent/agent.py)
   - Initialize Swarm client
   - Define agent with system instructions
   - Register MCP tools as agent functions
   - Configure context variables pattern

2. Create agent prompts (backend/src/agent/prompts.py)
   - Define system prompt for todo management
   - Include tool usage guidelines
   - Add error handling instructions
   - Define response formatting rules

3. Implement agent invocation function
   - Accept messages array and user_id
   - Build context_variables dict with user_id
   - Call client.run() with agent and context
   - Extract response messages and tool calls
   - Handle agent errors and timeouts

4. Add agent configuration
   - Add OPENAI_API_KEY to .env.example
   - Add OPENAI_MODEL to config (default: gpt-4)
   - Add AGENT_TIMEOUT to config (default: 30 seconds)
   - Add CONTEXT_WINDOW_SIZE to config (default: 20 messages)

**Acceptance Criteria**:
- Agent initialized with all 4 tools
- System prompt guides agent behavior
- Agent invokes tools correctly with user context
- Agent responses formatted for UI consumption
- Configuration externalized to .env
- Integration tests with real agent (mocked OpenAI API)

### Phase 4: Chat API Endpoint

**Objective**: Implement stateless chat endpoint with context loading

**Tasks**:
1. Create chat schemas (backend/src/schemas/chat.py)
   - ChatRequest: conversation_id (optional), message
   - ChatResponse: conversation_id, message, tool_calls, created_at
   - ToolCallSchema: id, name, arguments, result

2. Create conversation schemas (backend/src/schemas/conversation.py)
   - ConversationSchema: id, user_id, title, created_at, updated_at
   - ConversationDetailSchema: extends ConversationSchema, adds messages array
   - MessageSchema: id, conversation_id, role, content, tool_calls, created_at

3. Implement POST /api/chat endpoint (backend/src/api/chat.py)
   - Require JWT authentication
   - Load or create conversation
   - Save user message to database
   - Load conversation history (last 20 messages)
   - Invoke agent with full context
   - Save assistant response and tool calls
   - Return ChatResponse

4. Implement conversation history loading
   - Query messages by conversation_id
   - Order by created_at ASC
   - Limit to CONTEXT_WINDOW_SIZE (20)
   - Format as OpenAI messages array

5. Add error handling
   - Handle database errors (500)
   - Handle agent timeouts (504)
   - Handle invalid conversation_id (404)
   - Handle authentication errors (401)

**Acceptance Criteria**:
- Chat endpoint accepts messages and returns responses
- Conversation created on first message
- Context loaded from database on every request
- Agent invoked with full conversation history
- Tool calls saved to database
- Error responses follow API contract
- Integration tests for full chat flow

### Phase 5: Conversation Management Endpoints

**Objective**: Implement endpoints for listing and managing conversations

**Tasks**:
1. Implement GET /api/conversations (backend/src/api/conversations.py)
   - Require JWT authentication
   - Query conversations filtered by user_id
   - Order by updated_at DESC
   - Support pagination (limit, offset)
   - Return array of conversations with metadata

2. Implement GET /api/conversations/{conversation_id}
   - Require JWT authentication
   - Verify conversation ownership (user_id)
   - Load conversation with all messages
   - Return ConversationDetailSchema
   - Handle not found (404)

3. Implement DELETE /api/conversations/{conversation_id}
   - Require JWT authentication
   - Verify conversation ownership
   - Delete conversation and all messages (cascade)
   - Return 204 No Content
   - Handle not found (404)

4. Register routers in main.py
   - Add chat router with /api prefix
   - Add conversations router with /api prefix
   - Update OpenAPI docs

**Acceptance Criteria**:
- All conversation endpoints implemented
- User isolation enforced (can only access own conversations)
- Pagination works correctly
- Cascade delete removes messages
- API matches OpenAPI spec
- Integration tests for all endpoints

### Phase 6: Testing & Validation

**Objective**: Comprehensive testing of agent and API

**Tasks**:
1. Unit tests for MCP tools
   - Test each tool with valid inputs
   - Test user context enforcement
   - Test error cases (not found, permission denied)
   - Test database errors
   - Mock database with pytest fixtures

2. Integration tests for agent
   - Test agent with mocked OpenAI API
   - Verify tool invocations
   - Test multi-turn conversations
   - Test error handling
   - Test context window limits

3. API integration tests
   - Test full chat flow (create conversation, send messages)
   - Test conversation listing and retrieval
   - Test conversation deletion
   - Test authentication enforcement
   - Test user isolation (cross-user access blocked)

4. Performance tests
   - Measure chat response time
   - Measure tool execution time
   - Test concurrent chat sessions
   - Verify database query performance

5. Security tests
   - Verify JWT authentication required
   - Test cross-user access attempts (should fail)
   - Verify all queries filter by user_id
   - Test SQL injection attempts (should be blocked)

**Acceptance Criteria**:
- 100% test coverage for MCP tools
- Integration tests pass for agent and API
- Performance meets targets (<5s chat response)
- Security tests confirm user isolation
- All tests pass in CI/CD pipeline

### Phase 7: Documentation & Deployment

**Objective**: Complete documentation and prepare for deployment

**Tasks**:
1. Create quickstart.md
   - Setup instructions (dependencies, .env)
   - Database migration steps
   - Running the application
   - Testing the chat endpoint
   - Example curl commands

2. Update API documentation
   - Ensure OpenAPI spec is accurate
   - Add example requests/responses
   - Document error codes
   - Add authentication instructions

3. Update .env.example
   - Add OPENAI_API_KEY placeholder
   - Add OPENAI_MODEL with default
   - Add AGENT_TIMEOUT with default
   - Add CONTEXT_WINDOW_SIZE with default

4. Create deployment checklist
   - Database migration steps
   - Environment variable configuration
   - OpenAI API key setup
   - Health check endpoints
   - Monitoring and logging

**Acceptance Criteria**:
- quickstart.md enables new developers to run the app
- API documentation complete and accurate
- .env.example includes all required variables
- Deployment checklist covers all steps

## Risk Analysis

### High Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API rate limits | Chat unavailable during high load | Implement retry logic with exponential backoff, add rate limit monitoring |
| Agent timeout on complex queries | Poor user experience | Set 30s timeout, optimize tool execution, provide timeout error message |
| Context window overflow | Agent loses conversation history | Limit to 20 messages, implement smart truncation (keep first + last N) |
| Cross-user data leakage | Critical security vulnerability | Enforce user_id filtering in all tools, add security tests, code review |

### Medium Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection pool exhaustion | API errors under load | Configure connection pool size, add connection monitoring |
| Tool invocation logging failures | Lost audit trail | Make logging non-blocking, add fallback logging to file |
| Agent hallucination (incorrect tool calls) | Wrong tasks created/deleted | Add confirmation prompts in agent instructions, log all tool calls |
| Large conversation history queries | Slow response times | Add indexes on (conversation_id, created_at), limit context window |

### Low Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI model deprecation | Need to update model | Use environment variable for model selection, test with multiple models |
| Tool schema changes | Agent compatibility issues | Version tool schemas, maintain backward compatibility |
| Message content size limits | Truncated messages | Add validation for max message length (2000 chars) |

## Success Criteria

### Functional Requirements (from spec.md)

- ✅ FR-001: Agent interprets natural language and maps to tools
- ✅ FR-002: Agent uses MCP tools exclusively (no direct database access)
- ✅ FR-003: User context passed to every tool invocation
- ✅ FR-004: Agent validates tool responses and handles errors
- ✅ FR-005: Agent formats responses for user consumption
- ✅ FR-006: MCP tools are stateless with all context in parameters
- ✅ FR-007: Tools validate inputs against schemas
- ✅ FR-008: Tools return structured success/error responses
- ✅ FR-009: Tools enforce user isolation with user_id filtering
- ✅ FR-010: Tools handle database errors gracefully
- ✅ FR-011: Agent provides clear error messages
- ✅ FR-012: Responses structured for chat UI consumption
- ✅ FR-013: All tool invocations logged with user context
- ✅ FR-014: Agent handles ambiguous input appropriately
- ✅ FR-015: Tools complete within 5 seconds

### Measurable Outcomes (from spec.md)

- **SC-001**: Agent correctly maps user intent to tools with 95% accuracy
  - **Measurement**: Manual testing with 20 diverse user inputs
  - **Target**: 19/20 correct tool selections

- **SC-002**: Tool invocations complete within 5 seconds
  - **Measurement**: Performance tests with database queries
  - **Target**: p95 < 5s, p99 < 10s

- **SC-003**: 100% user-scoped data access (no leakage)
  - **Measurement**: Security tests attempting cross-user access
  - **Target**: All attempts blocked with 404/403

- **SC-004**: Clear error messages for 100% of failures
  - **Measurement**: Error handling tests for all failure modes
  - **Target**: All errors return user-friendly messages

- **SC-005**: Tool validation catches 100% of invalid inputs
  - **Measurement**: Unit tests with invalid parameters
  - **Target**: All invalid inputs rejected before database

- **SC-006**: Responses consumable by frontend without transformation
  - **Measurement**: API contract validation tests
  - **Target**: All responses match OpenAPI schema

- **SC-007**: Zero in-memory state between requests
  - **Measurement**: Architecture review and restart tests
  - **Target**: Application restarts without state loss

- **SC-008**: All tool operations auditable through logs
  - **Measurement**: Verify ToolInvocation records for all operations
  - **Target**: 100% of tool calls logged

## Dependencies

### External Dependencies
- OpenAI API (requires API key and billing account)
- Neon PostgreSQL (existing, no changes needed)
- OpenAI Python SDK (pip install openai)
- OpenAI Agents SDK / Swarm (pip install git+https://github.com/openai/swarm.git)

### Internal Dependencies
- Existing User model and authentication system (Phase I & II)
- Existing Todo model and CRUD operations (Phase I)
- Existing JWT authentication middleware (Phase II)
- Existing database connection and session management (Phase I)

### Blocking Dependencies
- None - all dependencies are available and stable

## Rollout Strategy

### Phase 1: Backend Implementation (This Feature)
1. Implement database schema and models
2. Implement MCP tools with user isolation
3. Implement AI agent with tool integration
4. Implement chat API endpoint
5. Implement conversation management endpoints
6. Complete testing and documentation

### Phase 2: Frontend Integration (Future Feature)
1. Create chat UI components with ChatKit
2. Integrate with chat API endpoint
3. Display tool calls and results
4. Add conversation history sidebar
5. Implement real-time updates (optional)

### Phase 3: Production Deployment (Future)
1. Configure OpenAI API key in production
2. Run database migrations
3. Deploy backend with environment variables
4. Monitor API performance and error rates
5. Collect user feedback and iterate

## Monitoring & Observability

### Key Metrics
- Chat response time (p50, p95, p99)
- Tool execution time per tool type
- Agent error rate
- OpenAI API error rate
- Tool invocation success rate
- Conversation creation rate
- Active conversations per user

### Logging
- All tool invocations logged to ToolInvocation table
- Agent errors logged with full context
- API errors logged with request details
- Performance metrics logged for slow queries

### Alerts
- Chat response time > 10s (p95)
- Agent error rate > 5%
- OpenAI API error rate > 10%
- Database connection pool exhaustion
- Tool invocation logging failures

## Next Steps

1. **Review this plan** with stakeholders
2. **Run `/sp.tasks`** to generate task breakdown
3. **Run `/sp.implement`** to execute tasks with specialized agents
4. **Validate against spec.md** after implementation
5. **Create PR** and request code review
6. **Deploy to staging** for testing
7. **Collect feedback** from hackathon judges

---

**Plan Status**: ✅ COMPLETE - Ready for task generation
**Constitution Check**: ✅ ALL GATES PASS
**Next Command**: `/sp.tasks` to generate actionable task list
