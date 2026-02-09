"""Manual test script for update_task tool.

This script tests the update_task MCP tool implementation without requiring
the full test suite infrastructure.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend/src to Python path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))


def test_update_task_no_auth():
    """Test update_task without user authentication."""
    from agent.tools import update_task

    # Test with no user_id
    result = update_task(
        context_variables={},
        task_id=1,
        is_completed=True
    )
    data = json.loads(result)

    print("Test: update_task without authentication")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "USER_NOT_AUTHENTICATED"
    print("PASSED\n")


def test_update_task_no_session():
    """Test update_task without database session."""
    from agent.tools import update_task

    # Test with user_id but no session
    result = update_task(
        context_variables={"user_id": 1},
        task_id=1,
        is_completed=True
    )
    data = json.loads(result)

    print("Test: update_task without database session")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("PASSED\n")


def test_update_task_no_fields():
    """Test update_task with no fields to update."""
    from agent.tools import update_task

    # Test with no update fields provided
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1
    )
    data = json.loads(result)

    print("Test: update_task with no fields to update")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "VALIDATION_ERROR"
    assert "No fields provided" in data["message"]
    print("PASSED\n")


def test_update_task_empty_title():
    """Test update_task with empty title."""
    from agent.tools import update_task

    # Test with empty title
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        title=""
    )
    data = json.loads(result)

    print("Test: update_task with empty title")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "VALIDATION_ERROR"
    assert "empty" in data["message"].lower()
    print("PASSED\n")


def test_update_task_title_too_long():
    """Test update_task with title exceeding max length."""
    from agent.tools import update_task

    # Test with title > 200 characters
    long_title = "x" * 201
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        title=long_title
    )
    data = json.loads(result)

    print("Test: update_task with title > 200 characters")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "VALIDATION_ERROR"
    assert "200" in data["message"]
    print("PASSED\n")


def test_update_task_description_too_long():
    """Test update_task with description exceeding max length."""
    from agent.tools import update_task

    # Test with description > 1000 characters
    long_description = "x" * 1001
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        description=long_description
    )
    data = json.loads(result)

    print("Test: update_task with description > 1000 characters")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "VALIDATION_ERROR"
    assert "1000" in data["message"]
    print("PASSED\n")


def test_update_task_valid_title():
    """Test update_task with valid title (will fail at DB level)."""
    from agent.tools import update_task

    # Test with valid title (no session, so will fail at DB)
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        title="Valid task title"
    )
    data = json.loads(result)

    print("Test: update_task with valid title (no DB)")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    # Should fail at database level, not validation
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("PASSED\n")


def test_update_task_multiple_fields():
    """Test update_task with multiple fields (will fail at DB level)."""
    from agent.tools import update_task

    # Test with multiple valid fields
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        title="Updated title",
        description="Updated description",
        is_completed=True
    )
    data = json.loads(result)

    print("Test: update_task with multiple fields (no DB)")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    # Should fail at database level, not validation
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("PASSED\n")


def test_response_structure():
    """Test that error responses have correct structure."""
    from agent.tools import update_task

    result = update_task(
        context_variables={},
        task_id=1,
        is_completed=True
    )
    data = json.loads(result)

    print("Test: Response structure validation")
    print(f"Has 'success' field: {'success' in data}")
    print(f"Has 'message' field: {'message' in data}")
    print(f"Has 'error' field: {'error' in data}")

    assert "success" in data
    assert "message" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    print("PASSED\n")


def test_partial_update_completion_only():
    """Test update_task with only completion status (will fail at DB level)."""
    from agent.tools import update_task

    # Test updating only completion status
    result = update_task(
        context_variables={"user_id": 1, "session": None},
        task_id=1,
        is_completed=True
    )
    data = json.loads(result)

    print("Test: update_task with only is_completed (no DB)")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    # Should fail at database level, not validation
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("PASSED\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing update_task MCP Tool Implementation")
    print("=" * 60 + "\n")

    try:
        test_update_task_no_auth()
        test_update_task_no_session()
        test_update_task_no_fields()
        test_update_task_empty_title()
        test_update_task_title_too_long()
        test_update_task_description_too_long()
        test_update_task_valid_title()
        test_update_task_multiple_fields()
        test_partial_update_completion_only()
        test_response_structure()

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
