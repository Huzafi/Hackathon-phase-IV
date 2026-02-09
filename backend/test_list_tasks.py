"""Manual test script for list_tasks tool.

This script tests the list_tasks MCP tool implementation without requiring
the full test suite infrastructure.
"""
import json
from typing import Dict, Any


def mock_context(user_id: int = 1) -> Dict[str, Any]:
    """Create a mock context with user_id but no session."""
    return {
        "user_id": user_id,
        "session": None,  # Will cause DATABASE_ERROR
    }


def test_list_tasks_no_auth():
    """Test list_tasks without user authentication."""
    from backend.src.agent.tools import list_tasks

    # Test with no user_id
    result = list_tasks(context_variables={})
    data = json.loads(result)

    print("Test: list_tasks without authentication")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "USER_NOT_AUTHENTICATED"
    print("✓ PASSED\n")


def test_list_tasks_no_session():
    """Test list_tasks without database session."""
    from backend.src.agent.tools import list_tasks

    # Test with user_id but no session
    result = list_tasks(context_variables={"user_id": 1})
    data = json.loads(result)

    print("Test: list_tasks without database session")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("✓ PASSED\n")


def test_list_tasks_with_filter():
    """Test list_tasks with completion filter parameter."""
    from backend.src.agent.tools import list_tasks

    # Test with completed filter (will fail due to no session, but validates parameter)
    result = list_tasks(context_variables={"user_id": 1}, completed=True)
    data = json.loads(result)

    print("Test: list_tasks with completed=True filter")
    print(f"Success: {data['success']}")
    print(f"Error: {data.get('error')}")
    assert data["success"] is False
    assert data["error"] == "DATABASE_ERROR"
    print("✓ PASSED\n")


def test_response_structure():
    """Test that error responses have correct structure."""
    from backend.src.agent.tools import list_tasks

    result = list_tasks(context_variables={})
    data = json.loads(result)

    print("Test: Response structure validation")
    print(f"Has 'success' field: {'success' in data}")
    print(f"Has 'message' field: {'message' in data}")
    print(f"Has 'error' field: {'error' in data}")

    assert "success" in data
    assert "message" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    print("✓ PASSED\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing list_tasks MCP Tool Implementation")
    print("=" * 60 + "\n")

    try:
        test_list_tasks_no_auth()
        test_list_tasks_no_session()
        test_list_tasks_with_filter()
        test_response_structure()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
