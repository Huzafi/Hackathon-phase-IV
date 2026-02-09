<!--
Sync Impact Report:
- Version: 1.0.0 → 1.1.0 (MINOR: Added AI agent principles for Phase III)
- Modified Principles:
  - IV. Clear Separation of Concerns → Expanded to include AI agents and MCP tools
- Added Sections:
  - VII. Stateless Architecture with Persistent State
  - VIII. AI Agents via MCP Tools Only
  - IX. Conversation Persistence and Context Rebuilding
- Removed Sections: None
- Technology Stack: Added ChatKit, OpenAI Agents SDK, Official MCP SDK
- Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section aligns with all principles
  ✅ spec-template.md - Requirements structure supports AI agent and stateless principles
  ✅ tasks-template.md - Task organization supports SDD workflow with AI agents
- Follow-up TODOs: None
- Rationale: Phase III introduces AI chatbot capabilities requiring stateless architecture,
  MCP tool integration, and conversation persistence. These are additive principles that
  extend (not replace) existing security and separation of concerns requirements.
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (SDD)

All implementation MUST follow written specifications. No code may be written without:
- A documented feature specification (`spec.md`)
- An architectural plan (`plan.md`)
- A task breakdown (`tasks.md`)

**Rationale**: Ensures all development is intentional, traceable, and aligned with
documented requirements. Prevents scope creep and undocumented features.

### II. Security-First Design

Security is non-negotiable and MUST be enforced at every layer:
- All API endpoints (except signup/signin) MUST require JWT authentication
- All database queries MUST filter by authenticated user ID
- Secrets MUST be stored in environment variables (never hardcoded)
- User data MUST be isolated (users can only access their own data)
- HTTP status codes MUST be explicit (401 for unauthorized, 403 for forbidden)

**Rationale**: Multi-user applications require strict security boundaries to prevent
data leaks and unauthorized access. Security cannot be retrofitted.

### III. Zero Manual Coding

All code MUST be generated through Claude Code with specialized agents:
- Frontend: `nextjs-frontend-builder` agent
- Backend: `fastapi-backend-dev` agent
- Database: `neon-db-specialist` agent
- Authentication: `auth-specialist` agent

Manual code edits outside Claude Code output are prohibited.

**Rationale**: Ensures consistency, traceability, and adherence to architectural
patterns. All code generation is documented and reproducible.

### IV. Clear Separation of Concerns

The application MUST maintain strict boundaries between layers:
- **Frontend**: Next.js App Router, consumes REST APIs only
- **Backend**: FastAPI, stateless, JWT-secured endpoints
- **Database**: Neon PostgreSQL, accessed only via SQLModel ORM
- **Authentication**: Better Auth with JWT, centralized identity management
- **AI Agents**: OpenAI Agents SDK, act only through MCP tools
- **MCP Tools**: Official MCP SDK, stateless, schema-driven operations

No layer may bypass or directly access another layer's internals.

**Rationale**: Separation enables independent testing, scaling, and maintenance.
Prevents tight coupling and architectural erosion. AI agents must be deterministic
and auditable through explicit tool usage.

### V. Multi-User Data Isolation

This is a multi-user application. Every feature MUST enforce user boundaries:
- Users MUST have individual accounts (signup/signin required)
- Users MUST only see and modify their own data
- All API endpoints MUST extract user ID from JWT token
- All database queries MUST include `WHERE user_id = <authenticated_user_id>`
- Unauthorized access attempts MUST return 401 or 403

**Rationale**: Data isolation is a fundamental requirement. Failure to enforce
user boundaries is a critical security vulnerability.

### VI. Environment-Based Configuration

All environment-specific values MUST be externalized:
- Database connection strings in `.env`
- JWT signing secrets in `.env`
- API keys and credentials in `.env`
- Never commit `.env` files to version control

**Rationale**: Prevents accidental exposure of secrets and enables deployment
across multiple environments (dev, staging, production).

### VII. Stateless Architecture with Persistent State

The application MUST be stateless between requests with all state in the database:
- No in-memory session state between API requests
- Chat endpoint MUST rebuild full context from database on every request
- Conversation history MUST be persisted in database
- Application MUST survive restarts without losing user context
- All user interactions MUST be recoverable from database state

**Rationale**: Stateless architecture enables horizontal scaling, simplifies deployment,
and ensures data durability. Users expect conversations to persist across sessions.

### VIII. AI Agents via MCP Tools Only

AI agents MUST act exclusively through MCP (Model Context Protocol) tools:
- Agents MAY NOT directly access database, filesystem, or external APIs
- All agent actions MUST be expressed as MCP tool invocations
- MCP tools MUST be stateless and schema-driven
- MCP tools MUST validate inputs and handle errors explicitly
- Agent behavior MUST be deterministic and auditable through tool logs

**Rationale**: Constraining agents to MCP tools ensures predictable, testable, and
auditable AI behavior. Direct access would create non-deterministic side effects.

### IX. Conversation Persistence and Context Rebuilding

Chat functionality MUST persist and rebuild conversation context:
- All user messages MUST be stored in database with timestamps
- All agent responses MUST be stored in database with tool invocations
- Chat endpoint MUST load conversation history from database on each request
- Context window MUST be reconstructed from persisted messages
- Users MUST be able to resume conversations after logout/restart

**Rationale**: Conversation persistence is essential for multi-turn interactions.
Rebuilding context from database ensures consistency and enables conversation recovery.

## Technology Stack

**Fixed Constraints** (non-negotiable):

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) | 16+ |
| Backend | FastAPI | Latest |
| ORM | SQLModel | Latest |
| Database | Neon Serverless PostgreSQL | Latest |
| Authentication | Better Auth (JWT) | Latest |
| AI Framework | OpenAI Agents SDK | Latest |
| MCP Integration | Official MCP SDK | Latest |
| Chat UI | ChatKit | Latest |
| Development | Claude Code + Spec-Kit Plus | Latest |

**Rationale**: Technology stack is fixed to ensure consistency, leverage specialized
agents, and maintain architectural coherence. Changes require constitutional amendment.

## Development Workflow

All features MUST follow the Spec-Driven Development (SDD) workflow:

1. **Specify** (`/sp.specify`): Create feature specification with user stories
2. **Plan** (`/sp.plan`): Generate architectural plan and design decisions
3. **Tasks** (`/sp.tasks`): Break down into actionable, testable tasks
4. **Implement** (`/sp.implement`): Execute tasks using specialized agents
5. **Review**: Validate against spec and acceptance criteria

**Checkpoints**:
- Spec must be approved before planning
- Plan must pass Constitution Check before task generation
- Tasks must reference spec requirements
- Implementation must satisfy all acceptance criteria

**Prohibited**:
- Skipping specification phase
- Manual coding outside Claude Code
- Implementing features not in spec
- Bypassing security requirements
- AI agents accessing resources without MCP tools
- Storing state in memory between requests

## Governance

### Amendment Process

This constitution supersedes all other practices. Amendments require:
1. Documented justification for the change
2. Impact analysis on existing features
3. Migration plan for affected code
4. Version bump following semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or expanded guidance
   - **PATCH**: Clarifications, wording fixes

### Compliance

All pull requests and code reviews MUST verify:
- Adherence to SDD workflow (spec → plan → tasks → implement)
- Security requirements enforced (JWT auth, user filtering)
- Separation of concerns maintained
- No manual code edits outside Claude Code
- Environment variables used for secrets
- Stateless architecture (no in-memory state between requests)
- AI agents use only MCP tools (no direct resource access)
- Conversation history persisted in database

### Complexity Justification

Any violation of constitutional principles MUST be justified in writing:
- Why the violation is necessary
- What simpler alternatives were rejected and why
- How the violation will be monitored and contained

Unjustified complexity will be rejected.

### Runtime Guidance

For day-to-day development guidance, refer to `CLAUDE.md` in the repository root.
The constitution defines **what** must be done; `CLAUDE.md` defines **how** to do it.

**Version**: 1.1.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-29
