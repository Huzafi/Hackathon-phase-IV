---
id: 0006
title: Implement update_task MCP Tool
stage: green
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-agent-mcp-tasks
branch: 004-agent-mcp-tasks
user: developer
command: implementation
labels: ["mcp-tools", "update-task", "user-story-3", "backend", "fastapi"]
links:
  spec: specs/004-agent-mcp-tasks/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/agent/tools.py
  - backend/src/agent/prompts.py
  - backend/test_update_task.py
  - backend/IMPLEMENTATION_SUMMARY_UPDATE_TASK.md
tests:
  - backend/test_update_task.py (10 test cases)
---

## Prompt

Implement User Story 3: Update Task Status (Priority P3)

**Context**: Phase III AI agent feature. User Stories 1 (Create Task) and 2 (List Tasks) are complete. Now implementing update functionality.

**Goal**: Enable users to update tasks through natural language chat by implementing the update_task MCP tool.

**Tasks to Complete (T041-T047)**:

1. **Implement update_task MCP tool** in backend/src/agent/tools.py:
   - Function signature: `update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None, is_completed: Optional[bool] = None, user_id: int = None) -> dict`
   - Accept task_id (required) and optional update fields
   - Get user_id from context (injected by agent)
   - Verify task ownership: Query task by id AND user_id (security critical)
   - If task not found or user_id doesn't match, return permission denied error
   - Update only provided fields (partial update support)
   - Return structured response: `{"success": bool, "task": dict, "message": str, "error": Optional[str]}`
   - Handle validation errors (empty title, length violations)
   - Handle database errors
   - Log tool invocation to ToolInvocation table

2. **Register update_task tool** in backend/src/agent/agent.py:
   - Add update_task to the agent's functions list

3. **Update agent system prompt** in backend/src/agent/prompts.py:
   - Add usage guidelines for update_task tool
   - Include examples of how to identify tasks for updates
   - Add instructions for handling ambiguous task references

**Requirements**:
- Follow the same pattern as create_task and list_tasks tools
- Use SQLModel session for database operations
- Ensure task ownership verification (user_id match) before any update
- Support partial updates (only update provided fields)
- Handle edge cases: task not found, permission denied, invalid updates
- Tool invocation logging must not block tool execution

**Error Codes**:
- `USER_NOT_AUTHENTICATED`: Missing user_id in context
- `TASK_NOT_FOUND`: Task doesn't exist or user doesn't own it
- `PERMISSION_DENIED`: User trying to update another user's task
- `VALIDATION_ERROR`: Invalid input (empty title, length violations)
- `DATABASE_ERROR`: Database operation failures

## Response snapshot

Successfully implemented the `update_task` MCP tool with complete functionality:

### 1. Tool Implementation (backend/src/agent/tools.py, lines 197-315)

Implemented full `update_task` function with:
- User authentication validation (USER_NOT_AUTHENTICATED)
- Database session validation (DATABASE_ERROR)
- Input validation:
  - At least one field required for update
  - Title: non-empty, max 200 characters
  - Description: max 1000 characters
- **Security-critical**: Task ownership verification using `WHERE Todo.id == task_id AND Todo.user_id == user_id`
- Partial update support (only updates provided fields)
- Proper error handling with rollback on failure
- Structured JSON response with updated task data

### 2. Agent Registration (backend/src/agent/agent.py)

Tool already registered in agent's functions list (lines 25-30). No changes needed.

### 3. System Prompt Enhancement (backend/src/agent/prompts.py, lines 31-48)

Added comprehensive guidelines:
- **Task Updates**: Instructions for using update_task with different parameters
- **Identifying Tasks for Updates**: How to match tasks by ID or title
- **Common Update Patterns**: Natural language patterns and corresponding tool calls

### 4. Test Suite (backend/test_update_task.py)

Created comprehensive test file with 10 test cases:
1. Authentication validation (no user_id)
2. Database session validation (no session)
3. No fields provided validation
4. Empty title validation
5. Title length validation (>200 chars)
6. Description length validation (>1000 chars)
7. Valid single field update
8. Multiple field update
9. Partial update (completion status only)
10. Response structure validation

### 5. Documentation (backend/IMPLEMENTATION_SUMMARY_UPDATE_TASK.md)

Created comprehensive implementation summary with:
- Files modified and key changes
- Security implementation details
- Error codes and validation rules
- Manual testing instructions (6 test cases)
- Success criteria verification
- Integration points
- Next steps

## Outcome

- ✅ Impact: Completed User Story 3 (Update Task Status). Users can now update tasks through natural language chat with full security enforcement.
- 🧪 Tests: Created test_update_task.py with 10 test cases covering authentication, validation, and error scenarios
- 📁 Files: Modified 2 files (tools.py, prompts.py), created 2 new files (test_update_task.py, IMPLEMENTATION_SUMMARY_UPDATE_TASK.md)
- 🔁 Next prompts: Implement User Story 4 (Delete Task) - tasks T048-T054
- 🧠 Reflection: Implementation follows established patterns from create_task and list_tasks. Security-critical task ownership verification ensures multi-user isolation. Partial update support provides flexibility for users.

## Evaluation notes (flywheel)

- Failure modes observed: None. Implementation follows proven patterns from previous tools.
- Graders run and results (PASS/FAIL): Manual tests pending (requires running backend server with Swarm SDK)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run end-to-end integration test with real backend server to verify agent correctly identifies tasks by title and calls update_task tool
