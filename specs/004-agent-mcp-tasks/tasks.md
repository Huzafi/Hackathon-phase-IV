# Tasks: AI Agent & MCP Task Operations


**Input**: Design documents from `/specs/004-agent-mcp-tasks/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/, research.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow web application structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install OpenAI Python SDK in backend/requirements.txt
- [X] T002 Install OpenAI Agents SDK (Swarm) in backend/requirements.txt
- [X] T003 [P] Add OpenAI configuration to backend/.env.example (OPENAI_API_KEY, OPENAI_MODEL, AGENT_TIMEOUT, CONTEXT_WINDOW_SIZE)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create Conversation model in backend/src/models/conversation.py with UUID id, user_id FK, title, created_at, updated_at
- [X] T005 [P] Create Message model in backend/src/models/message.py with id, conversation_id FK, role enum, content, tool_calls JSON, created_at
- [X] T006 [P] Create ToolInvocation model in backend/src/models/tool_invocation.py with id, message_id FK, conversation_id FK, user_id FK, tool_name, tool_arguments JSON, tool_result JSON, success, error_message, execution_time_ms, created_at
- [X] T007 Update database initialization in backend/src/core/database.py to include new models (Conversation, Message, ToolInvocation)
- [X] T008 [P] Create agent module directory structure backend/src/agent/ with __init__.py
- [X] T009 [P] Create agent prompts module in backend/src/agent/prompts.py with system prompt for todo management
- [X] T010 [P] Create agent initialization module in backend/src/agent/agent.py with Swarm client setup
- [X] T011 [P] Create MCP tools module skeleton in backend/src/agent/tools.py with tool helper functions
- [X] T012 [P] Create ChatRequest schema in backend/src/schemas/chat.py with conversation_id optional and message fields
- [X] T013 [P] Create ChatResponse schema in backend/src/schemas/chat.py with conversation_id, message, tool_calls, created_at
- [X] T014 [P] Create ToolCallSchema in backend/src/schemas/chat.py with id, name, arguments, result fields
- [X] T015 [P] Create ConversationSchema in backend/src/schemas/conversation.py with id, user_id, title, created_at, updated_at
- [X] T016 [P] Create MessageSchema in backend/src/schemas/conversation.py with id, conversation_id, role, content, tool_calls, created_at
- [X] T017 [P] Create ConversationDetailSchema in backend/src/schemas/conversation.py extending ConversationSchema with messages array
- [X] T018 Create chat API router skeleton in backend/src/api/chat.py with POST /api/chat endpoint structure
- [X] T019 [P] Create conversations API router in backend/src/api/conversations.py with GET, GET/{id}, DELETE/{id} endpoints
- [X] T020 Register chat router in backend/src/main.py with /api prefix
- [X] T021 Register conversations router in backend/src/main.py with /api prefix
- [X] T022 Add OpenAI configuration to backend/src/core/config.py (OPENAI_API_KEY, OPENAI_MODEL, AGENT_TIMEOUT, CONTEXT_WINDOW_SIZE)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through natural language chat by implementing the create_task MCP tool

**Independent Test**: Send "Create a task to buy groceries" to chat endpoint and verify (1) agent calls create_task tool, (2) task created in database, (3) agent returns confirmation

### Implementation for User Story 1

- [X] T023 [US1] Implement create_task MCP tool in backend/src/agent/tools.py with title, description parameters and user_id from context
- [X] T024 [US1] Add input validation for create_task tool using Pydantic schema
- [X] T025 [US1] Add database operation in create_task to insert Todo record filtered by user_id
- [X] T026 [US1] Add error handling in create_task for database failures and return structured error response
- [X] T027 [US1] Add tool invocation logging in create_task to ToolInvocation table
- [X] T028 [US1] Register create_task tool with agent in backend/src/agent/agent.py
- [X] T029 [US1] Implement conversation creation logic in backend/src/api/chat.py for new conversations
- [X] T030 [US1] Implement user message saving in backend/src/api/chat.py to Message table
- [X] T031 [US1] Implement conversation history loading in backend/src/api/chat.py (last 20 messages)
- [X] T032 [US1] Implement agent invocation in backend/src/api/chat.py with user_id in context_variables
- [X] T033 [US1] Implement assistant response saving in backend/src/api/chat.py with tool_calls to Message table
- [X] T034 [US1] Add error handling in chat endpoint for agent timeouts and database errors

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - List and Retrieve Tasks (Priority: P2)

**Goal**: Enable users to list their tasks through natural language chat by implementing the list_tasks MCP tool

**Independent Test**: Send "What are my tasks?" to chat endpoint and verify (1) agent calls list_tasks tool, (2) tool returns only user's tasks, (3) agent formats response clearly

### Implementation for User Story 2

- [X] T035 [P] [US2] Implement list_tasks MCP tool in backend/src/agent/tools.py with optional completed filter and user_id from context
- [X] T036 [P] [US2] Add database query in list_tasks to fetch todos filtered by user_id
- [X] T037 [P] [US2] Add error handling in list_tasks for empty results and database failures
- [X] T038 [P] [US2] Add tool invocation logging in list_tasks to ToolInvocation table
- [X] T039 [US2] Register list_tasks tool with agent in backend/src/agent/agent.py
- [X] T040 [US2] Update agent system prompt in backend/src/agent/prompts.py to include list_tasks usage guidelines

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Status (Priority: P3)

**Goal**: Enable users to update tasks through natural language chat by implementing the update_task MCP tool

**Independent Test**: Create a task, then send "Mark 'buy groceries' as complete" and verify (1) agent identifies correct task, (2) calls update_task tool, (3) returns confirmation

### Implementation for User Story 3

- [X] T041 [P] [US3] Implement update_task MCP tool in backend/src/agent/tools.py with task_id, optional title/description/is_completed, and user_id from context
- [X] T042 [P] [US3] Add task ownership verification in update_task (user_id match)
- [X] T043 [P] [US3] Add database update operation in update_task with user_id filtering
- [X] T044 [P] [US3] Add error handling in update_task for task not found and permission denied
- [X] T045 [P] [US3] Add tool invocation logging in update_task to ToolInvocation table
- [X] T046 [US3] Register update_task tool with agent in backend/src/agent/agent.py
- [X] T047 [US3] Update agent system prompt in backend/src/agent/prompts.py to include update_task usage guidelines

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Task (Priority: P4)

**Goal**: Enable users to delete tasks through natural language chat by implementing the delete_task MCP tool

**Independent Test**: Create a task, then send "Delete the groceries task" and verify (1) agent identifies correct task, (2) calls delete_task tool, (3) task removed from database

### Implementation for User Story 4

- [X] T048 [P] [US4] Implement delete_task MCP tool in backend/src/agent/tools.py with task_id and user_id from context
- [X] T049 [P] [US4] Add task ownership verification in delete_task (user_id match)
- [X] T050 [P] [US4] Add database delete operation in delete_task with user_id filtering
- [X] T051 [P] [US4] Add error handling in delete_task for task not found and permission denied
- [X] T052 [P] [US4] Add tool invocation logging in delete_task to ToolInvocation table
- [X] T053 [US4] Register delete_task tool with agent in backend/src/agent/agent.py
- [X] T054 [US4] Update agent system prompt in backend/src/agent/prompts.py to include delete_task usage guidelines

**Checkpoint**: All CRUD operations (create, list, update, delete) should now be functional through natural language

---

## Phase 7: User Story 5 - Error Handling and User Feedback (Priority: P5)

**Goal**: Ensure robust error handling across all tools and agent responses

**Independent Test**: Trigger error conditions (invalid task ID, database failure, unauthorized access) and verify (1) agent receives error responses, (2) translates to user-friendly messages

### Implementation for User Story 5

- [X] T055 [P] [US5] Add comprehensive error handling in create_task for validation errors, database errors, and authentication errors
- [X] T056 [P] [US5] Add comprehensive error handling in list_tasks for database errors and authentication errors
- [X] T057 [P] [US5] Add comprehensive error handling in update_task for validation errors, not found errors, permission errors, database errors
- [X] T058 [P] [US5] Add comprehensive error handling in delete_task for not found errors, permission errors, database errors
- [X] T059 [US5] Update agent system prompt in backend/src/agent/prompts.py to include error translation guidelines
- [X] T060 [US5] Add error response formatting in backend/src/api/chat.py for agent errors, timeouts, and database failures
- [X] T061 [US5] Add error response formatting in backend/src/api/conversations.py for not found and permission errors

**Checkpoint**: All user stories should now handle errors gracefully with clear user feedback

---

## Phase 8: Conversation Management (Supporting Features)

**Goal**: Implement conversation listing and deletion endpoints

**Purpose**: Enable users to manage their conversation history

- [X] T062 [P] Implement GET /api/conversations endpoint in backend/src/api/conversations.py with user_id filtering and pagination
- [X] T063 [P] Implement GET /api/conversations/{id} endpoint in backend/src/api/conversations.py with ownership verification
- [X] T064 [P] Implement DELETE /api/conversations/{id} endpoint in backend/src/api/conversations.py with cascade delete of messages

**Checkpoint**: Conversation management features complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, deployment preparation, and final validation

- [X] T065 [P] Update backend/.env.example with all required OpenAI configuration variables
- [X] T066 [P] Create deployment checklist in specs/004-agent-mcp-tasks/deployment.md
- [X] T067 [P] Verify all database queries include user_id filtering (security audit)
- [X] T068 [P] Verify all tool invocations are logged to ToolInvocation table (audit trail)
- [X] T069 Run manual validation of all user stories (US1-US5) with curl commands from quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Conversation Management (Phase 8)**: Depends on Foundational phase, can run in parallel with user stories
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (but builds on same infrastructure)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3
- **User Story 5 (P5)**: Should start after US1-US4 are implemented (enhances existing tools)

### Within Each User Story

- Tool implementation before agent registration
- Agent registration before testing through chat endpoint
- Error handling can be added incrementally

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- Conversation management (Phase 8) can run in parallel with user story phases

---

## Parallel Example: User Story 2

```bash
# Launch all implementation tasks for User Story 2 together:
Task: "Implement list_tasks MCP tool in backend/src/agent/tools.py"
Task: "Add database query in list_tasks to fetch todos filtered by user_id"
Task: "Add error handling in list_tasks for empty results and database failures"
Task: "Add tool invocation logging in list_tasks to ToolInvocation table"

# Then sequentially:
Task: "Register list_tasks tool with agent in backend/src/agent/agent.py"
Task: "Update agent system prompt to include list_tasks usage guidelines"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Task via Natural Language)
4. **STOP and VALIDATE**: Test User Story 1 independently with curl commands
5. Deploy/demo if ready - this is a working MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (create_task tool)
   - Developer B: User Story 2 (list_tasks tool)
   - Developer C: User Story 3 (update_task tool)
   - Developer D: User Story 4 (delete_task tool)
3. Stories complete and integrate independently
4. Developer E: User Story 5 (error handling across all tools)
5. All developers: Phase 8 (conversation management) and Phase 9 (polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 69
**Setup Tasks**: 3
**Foundational Tasks**: 19 (BLOCKING)
**User Story 1 (P1)**: 12 tasks
**User Story 2 (P2)**: 6 tasks
**User Story 3 (P3)**: 7 tasks
**User Story 4 (P4)**: 7 tasks
**User Story 5 (P5)**: 7 tasks
**Conversation Management**: 3 tasks
**Polish**: 5 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = 34 tasks for working MVP

**Independent Test Criteria**:
- US1: Create task via chat and verify in database
- US2: List tasks via chat and verify user-scoped results
- US3: Update task via chat and verify changes in database
- US4: Delete task via chat and verify removal from database
- US5: Trigger errors and verify user-friendly messages
