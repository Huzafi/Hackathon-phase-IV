# Conversation Management API - Manual Test Guide

## Overview
This guide provides manual test commands for the conversation management endpoints implemented in Phase 8.

## Prerequisites
- Backend server running (e.g., `uvicorn src.main:app --reload`)
- `curl` or similar HTTP client installed
- `jq` for JSON formatting (optional)

## Endpoints Implemented

### 1. GET /api/conversations
List all conversations for authenticated user with pagination and message counts.

**Features:**
- Pagination support (limit: 1-100, default 20; offset: default 0)
- Ordered by updated_at DESC (most recent first)
- Includes message_count for each conversation
- JWT authentication required
- User isolation enforced

### 2. GET /api/conversations/{conversation_id}
Get specific conversation with all messages.

**Features:**
- Returns conversation metadata
- Includes all messages ordered by created_at ASC
- JWT authentication required
- Ownership verification (404 if not owned)

### 3. DELETE /api/conversations/{conversation_id}
Delete conversation with cascade delete.

**Features:**
- Deletes conversation, messages, and tool_invocations
- Cascade delete order: tool_invocations → messages → conversation
- Returns 204 No Content on success
- JWT authentication required
- Ownership verification (404 if not owned)

## Manual Test Commands

### Step 1: Sign up and get JWT token

```bash
# Sign up a new user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_conv@example.com",
    "password": "testpass123"
  }' | jq

# Save the access_token from the response
export JWT_TOKEN="<your_access_token_here>"
```

### Step 2: Create a conversation (via chat endpoint)

```bash
# Send a chat message to create a conversation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "message": "Create a task to test conversation management"
  }' | jq

# Save the conversation_id from the response
export CONV_ID="<conversation_id_here>"
```

### Step 3: Send more messages to the conversation

```bash
# Send another message to the same conversation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "message": "List all my tasks",
    "conversation_id": "'$CONV_ID'"
  }' | jq
```

### Step 4: List conversations (with pagination and message_count)

```bash
# List all conversations (default pagination)
curl -X GET "http://localhost:8000/api/conversations" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# List with custom pagination
curl -X GET "http://localhost:8000/api/conversations?limit=10&offset=0" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# Expected response structure:
# {
#   "conversations": [
#     {
#       "id": "uuid",
#       "user_id": 1,
#       "title": "...",
#       "created_at": "...",
#       "updated_at": "...",
#       "message_count": 5  <-- NEW FIELD
#     }
#   ],
#   "total": 1,
#   "limit": 20,
#   "offset": 0
# }
```

### Step 5: Get specific conversation with messages

```bash
# Get conversation details with all messages
curl -X GET "http://localhost:8000/api/conversations/$CONV_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# Expected response structure:
# {
#   "id": "uuid",
#   "user_id": 1,
#   "title": "...",
#   "created_at": "...",
#   "updated_at": "...",
#   "message_count": 5,
#   "messages": [
#     {
#       "id": 1,
#       "conversation_id": "uuid",
#       "role": "user",
#       "content": "...",
#       "tool_calls": null,
#       "created_at": "..."
#     },
#     ...
#   ]
# }
```

### Step 6: Test unauthorized access (should return 404)

```bash
# Try to access non-existent conversation
curl -X GET "http://localhost:8000/api/conversations/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# Expected: 404 Not Found
# {
#   "detail": "Conversation not found"
# }
```

### Step 7: Delete conversation

```bash
# Delete the conversation
curl -X DELETE "http://localhost:8000/api/conversations/$CONV_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -v

# Expected: 204 No Content (empty response body)
```

### Step 8: Verify deletion

```bash
# Try to get the deleted conversation
curl -X GET "http://localhost:8000/api/conversations/$CONV_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# Expected: 404 Not Found
# {
#   "detail": "Conversation not found"
# }

# Verify it's not in the list
curl -X GET "http://localhost:8000/api/conversations" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

# The deleted conversation should not appear in the list
```

## Security Verification

### Test 1: No authentication (should fail)
```bash
curl -X GET "http://localhost:8000/api/conversations" | jq
# Expected: 401 Unauthorized
```

### Test 2: Invalid token (should fail)
```bash
curl -X GET "http://localhost:8000/api/conversations" \
  -H "Authorization: Bearer invalid_token" | jq
# Expected: 401 Unauthorized
```

### Test 3: Cross-user access (should return 404)
```bash
# Sign up another user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_conv2@example.com",
    "password": "testpass123"
  }' | jq

export JWT_TOKEN2="<second_user_token>"

# Try to access first user's conversation
curl -X GET "http://localhost:8000/api/conversations/$CONV_ID" \
  -H "Authorization: Bearer $JWT_TOKEN2" | jq

# Expected: 404 Not Found (not 403, to prevent information leakage)
```

## Cascade Delete Verification

To verify that cascade delete works properly (deletes tool_invocations, messages, and conversation):

1. Create a conversation with multiple messages and tool invocations
2. Query the database directly to see the records:
   ```sql
   SELECT COUNT(*) FROM messages WHERE conversation_id = '<conv_id>';
   SELECT COUNT(*) FROM tool_invocations WHERE conversation_id = '<conv_id>';
   ```
3. Delete the conversation via API
4. Query again to verify all records are deleted:
   ```sql
   SELECT COUNT(*) FROM messages WHERE conversation_id = '<conv_id>';  -- Should be 0
   SELECT COUNT(*) FROM tool_invocations WHERE conversation_id = '<conv_id>';  -- Should be 0
   SELECT COUNT(*) FROM conversations WHERE id = '<conv_id>';  -- Should be 0
   ```

## Expected Behavior Summary

| Endpoint | Auth Required | User Isolation | Status Codes |
|----------|---------------|----------------|--------------|
| GET /api/conversations | Yes | Yes | 200, 401 |
| GET /api/conversations/{id} | Yes | Yes | 200, 404, 401 |
| DELETE /api/conversations/{id} | Yes | Yes | 204, 404, 401 |

## Implementation Details

### Files Modified
- `backend/src/schemas/conversation.py` - Added message_count field to ConversationSchema
- `backend/src/api/conversations.py` - Updated list_conversations to include message counts and delete_conversation to cascade delete tool_invocations

### Key Features
1. **Pagination**: Supports limit (1-100, default 20) and offset (default 0)
2. **Message Count**: Each conversation in the list includes the number of messages
3. **Cascade Delete**: Deletes in order: tool_invocations → messages → conversation
4. **Security**: All endpoints require JWT auth and enforce user isolation
5. **Error Handling**: Returns 404 (not 403) for unauthorized access to prevent information leakage

### Database Queries
- List conversations: Filters by user_id, orders by updated_at DESC
- Count messages: Uses COUNT() for each conversation
- Delete cascade: Explicitly deletes tool_invocations, messages, then conversation
