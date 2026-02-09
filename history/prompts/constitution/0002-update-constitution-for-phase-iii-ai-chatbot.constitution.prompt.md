---
id: 0002
title: Update constitution for Phase III AI chatbot
stage: constitution
date: 2026-01-29
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: 003-frontend-integration
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "stateless-architecture", "mcp-tools", "conversation-persistence"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text
/sp.constitution

Project: Todo AI Chatbot (Phase III)

Core principles:
- Spec-driven, agentic development
- Stateless architecture with persistent database state
- Clear separation between UI, agents, MCP tools, and storage
- Deterministic AI behavior via explicit MCP tool usage
- Security-first, user-scoped operations

Key standards:
- AI agents may act only through MCP tools
- MCP tools must be stateless and schema-driven
- Chat endpoint must rebuild context from database every request
- All operations require authenticated user context
- Errors must be handled clearly and safely

Constraints:
- Stack is fixed: ChatKit, FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon PostgreSQL, Better Auth
- No in-memory state between requests
- No manual coding outside Claude Code
- Multi-user support is mandatory

Success criteria:
- Users manage todos via natural language
- Agent correctly maps intent to MCP tools
- Conversation persists across restarts
- Users can access only their own data
```

## Response snapshot

Updated constitution from version 1.0.0 to 1.1.0 (MINOR version bump) to incorporate Phase III AI chatbot requirements.

**Changes Made:**

1. **Modified Principle IV (Clear Separation of Concerns)**:
   - Added AI Agents layer (OpenAI Agents SDK, act only through MCP tools)
   - Added MCP Tools layer (Official MCP SDK, stateless, schema-driven operations)

2. **Added Three New Principles**:
   - **Principle VII: Stateless Architecture with Persistent State** - Requires no in-memory state between requests, chat endpoint rebuilds context from database, conversation history persisted
   - **Principle VIII: AI Agents via MCP Tools Only** - Constrains agents to act exclusively through MCP tools, no direct resource access
   - **Principle IX: Conversation Persistence and Context Rebuilding** - Requires all messages stored in database, context reconstructed on each request

3. **Updated Technology Stack**:
   - Added: ChatKit, OpenAI Agents SDK, Official MCP SDK

4. **Updated Development Workflow Prohibitions**:
   - Added: AI agents accessing resources without MCP tools
   - Added: Storing state in memory between requests

5. **Updated Compliance Checklist**:
   - Added: Stateless architecture verification
   - Added: AI agents use only MCP tools verification
   - Added: Conversation history persistence verification

**Version Bump Rationale**: MINOR (1.0.0 → 1.1.0) because new principles were added without removing or making backward-incompatible changes to existing principles. Phase III extends the architecture rather than replacing it.

**Template Consistency**: Verified that plan-template.md, spec-template.md, and tasks-template.md all align with the updated principles.

## Outcome

- ✅ Impact: Constitution updated to version 1.1.0 with three new principles for AI chatbot architecture
- 🧪 Tests: N/A (constitutional amendments don't have automated tests)
- 📁 Files: Modified .specify/memory/constitution.md
- 🔁 Next prompts: `/sp.specify` to create Phase III feature specification, then `/sp.plan` for architectural planning
- 🧠 Reflection: MINOR version bump appropriate as Phase III principles are additive and extend existing security/separation principles without breaking changes

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update followed template structure and semantic versioning correctly
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, version incremented correctly, sync impact report complete)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - constitution updates are infrequent and deliberate
