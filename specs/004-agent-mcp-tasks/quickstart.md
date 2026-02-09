# Quickstart Guide: AI Agent & MCP Task Operations

**Feature**: 004-agent-mcp-tasks
**Date**: 2026-01-29
**Status**: Development Guide

## Overview

This guide helps developers set up and test the AI agent with MCP tools for natural language task management.

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon Serverless)
- OpenAI API account with billing enabled
- Existing Todo Backend API (Phase I & II)

## Setup Instructions

### 1. Install Dependencies

Add new dependencies to `backend/requirements.txt`:

```txt
# Existing dependencies
fastapi
sqlmodel
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
psycopg2-binary

# NEW: AI Agent dependencies
openai>=1.0.0
git+https://github.com/openai/swarm.git
```

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Update `backend/.env` with OpenAI configuration:

```env
# Existing variables
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# NEW: OpenAI Agent Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
AGENT_TIMEOUT=30
CONTEXT_WINDOW_SIZE=20
```

**Get OpenAI API Key**:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key to `.env` file
4. Ensure billing is enabled on your OpenAI account

### 3. Run Database Migrations

Create new database tables:

```bash
cd backend
python -m src.core.database
```

This will create:
- `conversations` table
- `messages` table
- `tool_invocations` table

Verify tables created:

```sql
-- Connect to your database
psql $DATABASE_URL

-- List tables
\dt

-- Should see:
-- users
-- todos
-- conversations
-- messages
-- tool_invocations
```

### 4. Start the Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

Server should start at `http://localhost:8000`

### 5. Verify API Documentation

Open browser to `http://localhost:8000/docs`

You should see new endpoints:
- `POST /api/chat` - Send chat message
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation details
- `DELETE /api/conversations/{id}` - Delete conversation

## Testing the Chat Endpoint

### 1. Create User Account (if not exists)

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 2. Sign In and Get JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` for subsequent requests.

### 3. Send Chat Message (Create Task)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": null,
    "message": "Create a task to buy groceries"
  }'
```

Expected Response:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I've created a task for you: 'Buy groceries'",
  "tool_calls": [
    {
      "id": "call_abc123",
      "name": "create_task",
      "arguments": {
        "title": "Buy groceries"
      },
      "result": {
        "success": true,
        "message": "Task created successfully",
        "data": {
          "task_id": 1,
          "title": "Buy groceries",
          "is_completed": false
        }
      }
    }
  ],
  "created_at": "2026-01-29T10:30:00Z"
}
```

### 4. List Tasks via Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "What are my tasks?"
  }'
```

Expected Response:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "You have 1 task:\n1. Buy groceries (not completed)",
  "tool_calls": [
    {
      "id": "call_def456",
      "name": "list_tasks",
      "arguments": {},
      "result": {
        "success": true,
        "message": "Retrieved 1 task",
        "data": {
          "tasks": [
            {
              "id": 1,
              "title": "Buy groceries",
              "description": null,
              "is_completed": false,
              "created_at": "2026-01-29T10:30:00Z",
              "updated_at": "2026-01-29T10:30:00Z"
            }
          ],
          "total": 1
        }
      }
    }
  ],
  "created_at": "2026-01-29T10:31:00Z"
}
```

### 5. Update Task via Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Mark the groceries task as complete"
  }'
```

### 6. Delete Task via Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Delete the groceries task"
  }'
```

## Testing Conversation Management

### List All Conversations

```bash
curl -X GET http://localhost:8000/api/conversations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Conversation Details

```bash
curl -X GET http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Delete Conversation

```bash
curl -X DELETE http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Running Tests

### Unit Tests (MCP Tools)

```bash
cd backend
pytest tests/test_agent/test_tools.py -v
```

### Integration Tests (Agent)

```bash
pytest tests/test_agent/test_agent.py -v
```

### API Tests (Chat Endpoint)

```bash
pytest tests/test_api/test_chat.py -v
pytest tests/test_api/test_conversations.py -v
```

### All Tests

```bash
pytest -v
```

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**: Ensure `OPENAI_API_KEY` is set in `.env` file and server is restarted.

```bash
# Check if variable is loaded
python -c "from src.core.config import settings; print(settings.OPENAI_API_KEY)"
```

### Issue: "Agent timeout"

**Solution**: Increase `AGENT_TIMEOUT` in `.env` or optimize tool execution.

```env
AGENT_TIMEOUT=60  # Increase to 60 seconds
```

### Issue: "Database connection error"

**Solution**: Verify `DATABASE_URL` is correct and database is accessible.

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Issue: "Tool invocation failed"

**Solution**: Check tool invocation logs in `tool_invocations` table.

```sql
SELECT * FROM tool_invocations
WHERE success = false
ORDER BY created_at DESC
LIMIT 10;
```

### Issue: "Cross-user data access"

**Solution**: Verify all tools filter by `user_id`. Check security tests.

```bash
pytest tests/test_api/test_chat.py::test_cross_user_access -v
```

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/src/agent/` or `backend/src/api/`

### 2. Run Tests

```bash
pytest tests/ -v
```

### 3. Test Manually

Use curl commands above or Postman to test endpoints

### 4. Check Logs

```bash
# View server logs
tail -f backend/logs/app.log

# View tool invocations
psql $DATABASE_URL -c "SELECT * FROM tool_invocations ORDER BY created_at DESC LIMIT 10;"
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: implement AI agent with MCP tools"
git push origin 004-agent-mcp-tasks
```

## Performance Monitoring

### Check Chat Response Time

```bash
# Add timing to curl
time curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"message": "Create a task to test performance"}'
```

Target: < 5 seconds

### Check Tool Execution Time

```sql
SELECT
  tool_name,
  AVG(execution_time_ms) as avg_time,
  MAX(execution_time_ms) as max_time,
  COUNT(*) as invocations
FROM tool_invocations
GROUP BY tool_name;
```

Target: < 2 seconds per tool

### Check Database Query Performance

```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE conversation_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at ASC
LIMIT 20;
```

Should use index on (conversation_id, created_at)

## Security Checklist

- [ ] JWT authentication required for all endpoints
- [ ] All database queries filter by `user_id`
- [ ] OpenAI API key stored in `.env` (not committed)
- [ ] Cross-user access blocked (verified by tests)
- [ ] SQL injection prevented (parameterized queries)
- [ ] Tool invocations logged for audit trail

## Next Steps

1. **Frontend Integration**: Build chat UI with ChatKit (future feature)
2. **Production Deployment**: Deploy to staging environment
3. **Performance Optimization**: Add caching, optimize queries
4. **Monitoring**: Set up alerts for errors and slow responses
5. **User Feedback**: Collect feedback from hackathon judges

## Resources

- [OpenAI Agents SDK (Swarm)](https://github.com/openai/swarm)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [API Contracts](./contracts/chat-api.yaml)
- [MCP Tools Schema](./contracts/mcp-tools.md)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review implementation plan in `plan.md`
3. Check API documentation at `/docs`
4. Review tool invocation logs in database
5. Contact development team
