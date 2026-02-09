# Deployment Checklist: AI Agent & MCP Task Operations

**Feature**: 004-agent-mcp-tasks
**Date**: 2026-01-30
**Status**: Ready for Deployment

## Overview

This checklist covers all steps required to deploy the AI Agent & MCP Task Operations feature to production. Follow these steps in order to ensure a successful deployment.

## Prerequisites

- [ ] Python 3.11+ installed on target server
- [ ] PostgreSQL database accessible (Neon Serverless PostgreSQL)
- [ ] OpenAI API account with billing enabled
- [ ] Valid OpenAI API key
- [ ] Existing authentication system deployed (JWT-based)
- [ ] Existing Todo CRUD endpoints deployed

## 1. Environment Configuration

### 1.1 Database Configuration

- [ ] Verify DATABASE_URL is set in production environment
- [ ] Test database connectivity from application server
- [ ] Verify SSL mode is enabled for Neon connection

**Example DATABASE_URL format:**
```
postgresql://user:password@host.neon.tech/dbname?sslmode=require&channel_binding=require
```

### 1.2 JWT Configuration

- [ ] Verify JWT_SECRET is set (existing from Phase II)
- [ ] Verify JWT_ALGORITHM is set (default: HS256)
- [ ] Verify JWT_EXPIRATION_HOURS is set (default: 24)

### 1.3 OpenAI Configuration

- [ ] Set OPENAI_API_KEY with valid API key
- [ ] Set OPENAI_MODEL (recommended: gpt-4 or gpt-4-turbo)
- [ ] Set AGENT_TIMEOUT (default: 30 seconds)
- [ ] Set CONTEXT_WINDOW_SIZE (default: 20 messages)

**Required environment variables:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
AGENT_TIMEOUT=30
CONTEXT_WINDOW_SIZE=20
```

**Security Note**: Never commit OPENAI_API_KEY to version control. Use secure secret management (e.g., AWS Secrets Manager, Azure Key Vault, environment variables).

## 2. Database Migration

### 2.1 Backup Current Database

- [ ] Create database backup before migration
- [ ] Verify backup is accessible and restorable
- [ ] Document backup location and timestamp

**Backup command (example):**
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2.2 Run Database Migrations

The following tables need to be created:

**Conversation Table:**
```sql
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_user_updated ON conversation(user_id, updated_at DESC);
```

**Message Table:**
```sql
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_conversation_created ON message(conversation_id, created_at ASC);
CREATE INDEX idx_message_created_at ON message(created_at DESC);
```

**ToolInvocation Table:**
```sql
CREATE TABLE tool_invocation (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    tool_arguments JSONB NOT NULL,
    tool_result JSONB NOT NULL,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    execution_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tool_invocation_user_id ON tool_invocation(user_id);
CREATE INDEX idx_tool_invocation_tool_name ON tool_invocation(tool_name, created_at DESC);
CREATE INDEX idx_tool_invocation_conversation_id ON tool_invocation(conversation_id);
CREATE INDEX idx_tool_invocation_message_id ON tool_invocation(message_id);
```

**Migration Steps:**
- [ ] Review migration SQL scripts
- [ ] Test migration on staging database first
- [ ] Run migration on production database
- [ ] Verify all tables created successfully
- [ ] Verify all indexes created successfully
- [ ] Verify foreign key constraints are active

**Verification queries:**
```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversation', 'message', 'tool_invocation');

-- Verify indexes exist
SELECT indexname FROM pg_indexes
WHERE tablename IN ('conversation', 'message', 'tool_invocation');

-- Verify foreign keys
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f'
AND conrelid::regclass::text IN ('conversation', 'message', 'tool_invocation');
```

### 2.3 Rollback Plan

If migration fails:
- [ ] Restore database from backup
- [ ] Document failure reason
- [ ] Fix migration scripts
- [ ] Retry migration

**Rollback command (example):**
```bash
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
```

## 3. Dependency Installation

### 3.1 Install Python Dependencies

- [ ] Update requirements.txt with new dependencies
- [ ] Install dependencies in virtual environment

**Required new dependencies:**
```txt
openai>=1.0.0
git+https://github.com/openai/swarm.git
```

**Installation commands:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 Verify Dependencies

- [ ] Verify OpenAI SDK installed: `pip show openai`
- [ ] Verify Swarm SDK installed: `pip show swarm`
- [ ] Run `pip list` to confirm all dependencies

## 4. Application Deployment

### 4.1 Deploy Backend Code

- [ ] Pull latest code from branch `004-agent-mcp-tasks`
- [ ] Verify all new files are present:
  - `backend/src/agent/__init__.py`
  - `backend/src/agent/agent.py`
  - `backend/src/agent/tools.py`
  - `backend/src/agent/prompts.py`
  - `backend/src/api/chat.py`
  - `backend/src/api/conversations.py`
  - `backend/src/models/conversation.py`
  - `backend/src/models/message.py`
  - `backend/src/models/tool_invocation.py`
  - `backend/src/schemas/chat.py`
  - `backend/src/schemas/conversation.py`

### 4.2 Update Application Configuration

- [ ] Update `backend/src/core/config.py` with OpenAI settings
- [ ] Verify all environment variables are loaded correctly
- [ ] Test configuration loading: `python -c "from src.core.config import settings; print(settings.OPENAI_MODEL)"`

### 4.3 Start Application Server

- [ ] Stop existing application server
- [ ] Start application with new code
- [ ] Verify server starts without errors
- [ ] Check logs for startup messages

**Start command (example with uvicorn):**
```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Production start command (with gunicorn):**
```bash
cd backend
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 5. Health Checks

### 5.1 API Health Check

- [ ] Verify API is responding: `curl http://localhost:8000/health`
- [ ] Verify OpenAPI docs accessible: `http://localhost:8000/docs`
- [ ] Verify new endpoints are registered:
  - POST `/api/chat`
  - GET `/api/conversations`
  - GET `/api/conversations/{id}`
  - DELETE `/api/conversations/{id}`

### 5.2 Database Connectivity

- [ ] Test database connection from application
- [ ] Verify all models can be queried
- [ ] Test creating a test conversation (then delete)

**Test query:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me?"}'
```

### 5.3 OpenAI API Connectivity

- [ ] Verify OpenAI API key is valid
- [ ] Test agent invocation with simple message
- [ ] Check logs for OpenAI API responses
- [ ] Verify no rate limit errors

**Test command:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to test deployment"}'
```

Expected response should include:
- `conversation_id` (UUID)
- `message` (agent response)
- `tool_calls` (array with create_task invocation)
- `created_at` (timestamp)

## 6. Functional Testing

### 6.1 Test User Story 1: Create Task

- [ ] Send message: "Create a task to buy groceries"
- [ ] Verify agent calls create_task tool
- [ ] Verify task created in database
- [ ] Verify agent returns confirmation message

### 6.2 Test User Story 2: List Tasks

- [ ] Send message: "What are my tasks?"
- [ ] Verify agent calls list_tasks tool
- [ ] Verify only user's tasks returned
- [ ] Verify agent formats response clearly

### 6.3 Test User Story 3: Update Task

- [ ] Send message: "Mark 'buy groceries' as complete"
- [ ] Verify agent calls update_task tool
- [ ] Verify task updated in database
- [ ] Verify agent returns confirmation

### 6.4 Test User Story 4: Delete Task

- [ ] Send message: "Delete the groceries task"
- [ ] Verify agent calls delete_task tool
- [ ] Verify task deleted from database
- [ ] Verify agent returns confirmation

### 6.5 Test User Story 5: Error Handling

- [ ] Test with invalid task ID
- [ ] Test with database connection failure (simulate)
- [ ] Test with unauthorized access attempt
- [ ] Verify all errors return user-friendly messages

### 6.6 Test Conversation Management

- [ ] List conversations: GET `/api/conversations`
- [ ] Get specific conversation: GET `/api/conversations/{id}`
- [ ] Delete conversation: DELETE `/api/conversations/{id}`
- [ ] Verify cascade delete removes messages and tool_invocations

## 7. Security Verification

### 7.1 Authentication

- [ ] Verify all endpoints require JWT authentication
- [ ] Test with invalid JWT token (should return 401)
- [ ] Test with expired JWT token (should return 401)
- [ ] Test without Authorization header (should return 401)

### 7.2 User Isolation

- [ ] Create tasks as User A
- [ ] Try to access User A's tasks as User B (should fail)
- [ ] Verify all database queries filter by user_id
- [ ] Verify no cross-user data leakage

### 7.3 Input Validation

- [ ] Test with empty message (should be rejected)
- [ ] Test with very long message (should be truncated or rejected)
- [ ] Test with special characters in task title
- [ ] Test with SQL injection attempts (should be blocked)

## 8. Performance Testing

### 8.1 Response Time

- [ ] Measure chat response time (target: < 5 seconds)
- [ ] Measure tool execution time (target: < 2 seconds)
- [ ] Test with 10 concurrent requests
- [ ] Verify no timeouts or errors

### 8.2 Database Performance

- [ ] Check query execution times in logs
- [ ] Verify indexes are being used (EXPLAIN ANALYZE)
- [ ] Monitor connection pool usage
- [ ] Verify no connection leaks

### 8.3 OpenAI API Performance

- [ ] Monitor OpenAI API response times
- [ ] Check for rate limit warnings
- [ ] Verify retry logic works on transient failures
- [ ] Monitor API usage and costs

## 9. Monitoring & Logging

### 9.1 Application Logs

- [ ] Configure log level (INFO for production)
- [ ] Verify logs are being written
- [ ] Check for error messages in logs
- [ ] Set up log aggregation (e.g., CloudWatch, Datadog)

**Key log patterns to monitor:**
- `Error creating task:`
- `Error listing tasks:`
- `Error updating task:`
- `Error deleting task:`
- `Chat endpoint error:`
- `Failed to log tool invocation:`

### 9.2 Metrics

Set up monitoring for:
- [ ] Chat response time (p50, p95, p99)
- [ ] Tool execution time per tool type
- [ ] Agent error rate
- [ ] OpenAI API error rate
- [ ] Tool invocation success rate
- [ ] Conversation creation rate
- [ ] Active conversations per user

### 9.3 Alerts

Configure alerts for:
- [ ] Chat response time > 10s (p95)
- [ ] Agent error rate > 5%
- [ ] OpenAI API error rate > 10%
- [ ] Database connection pool exhaustion
- [ ] Tool invocation logging failures
- [ ] Application server down

## 10. Documentation

### 10.1 API Documentation

- [ ] Verify OpenAPI docs are up to date: `/docs`
- [ ] Document all new endpoints
- [ ] Add example requests and responses
- [ ] Document error codes and messages

### 10.2 Runbook

- [ ] Document how to restart application
- [ ] Document how to check logs
- [ ] Document how to rollback deployment
- [ ] Document common troubleshooting steps

### 10.3 User Documentation

- [ ] Create user guide for chat interface (if applicable)
- [ ] Document supported commands and intents
- [ ] Provide example conversations
- [ ] Document error messages and resolutions

## 11. Post-Deployment Validation

### 11.1 Smoke Tests

- [ ] Run all functional tests again in production
- [ ] Verify no regressions in existing features
- [ ] Test with real user accounts
- [ ] Monitor for 1 hour after deployment

### 11.2 User Acceptance

- [ ] Have stakeholders test the feature
- [ ] Collect feedback on agent responses
- [ ] Verify all user stories are satisfied
- [ ] Document any issues or improvements needed

### 11.3 Rollback Decision

If critical issues are found:
- [ ] Document the issue
- [ ] Decide: fix forward or rollback?
- [ ] If rollback: restore database backup and previous code
- [ ] If fix forward: deploy hotfix and retest

## 12. Cleanup

### 12.1 Remove Test Data

- [ ] Delete test conversations created during testing
- [ ] Delete test tasks created during testing
- [ ] Verify no test users remain in production

### 12.2 Update Documentation

- [ ] Mark deployment as complete
- [ ] Update deployment history
- [ ] Document any issues encountered
- [ ] Update runbook with lessons learned

## Troubleshooting

### Common Issues

**Issue: OpenAI API key invalid**
- Verify OPENAI_API_KEY is set correctly
- Check API key has not expired
- Verify billing is enabled on OpenAI account

**Issue: Database connection fails**
- Verify DATABASE_URL is correct
- Check network connectivity to Neon
- Verify SSL mode is enabled
- Check database credentials

**Issue: Agent timeout**
- Increase AGENT_TIMEOUT value
- Check OpenAI API response times
- Verify network connectivity
- Check for rate limiting

**Issue: Tool invocation fails**
- Check database connectivity
- Verify user_id is being passed correctly
- Check tool input validation
- Review tool error logs

**Issue: Cross-user data leakage**
- CRITICAL: Immediately rollback deployment
- Review all database queries for user_id filtering
- Run security audit
- Fix and redeploy

## Success Criteria

Deployment is successful when:
- ✅ All database migrations completed without errors
- ✅ All environment variables configured correctly
- ✅ Application starts without errors
- ✅ All health checks pass
- ✅ All functional tests pass
- ✅ All security tests pass
- ✅ Performance meets targets (< 5s response time)
- ✅ Monitoring and alerts configured
- ✅ No critical issues found in post-deployment validation

## Rollback Procedure

If deployment fails:

1. **Stop application server**
2. **Restore database from backup**
   ```bash
   psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
   ```
3. **Revert code to previous version**
   ```bash
   git checkout main
   git pull origin main
   ```
4. **Restart application server**
5. **Verify previous version is working**
6. **Document failure reason**
7. **Plan fix and retry deployment**

## Contact Information

**Deployment Lead**: [Name]
**Database Admin**: [Name]
**DevOps Engineer**: [Name]
**On-Call Engineer**: [Name]

**Emergency Contacts**:
- Slack: #deployments
- Email: deployments@company.com
- Phone: [Emergency number]

---

**Deployment Checklist Version**: 1.0
**Last Updated**: 2026-01-30
**Next Review**: After first production deployment
