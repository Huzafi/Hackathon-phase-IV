"""
MCP tools for task management operations.

All tools are stateless and create their own database sessions.
Each tool receives only user_id from context_variables and handles
its own database lifecycle to avoid serialization issues.
"""

from typing import Optional, Dict, Any
import json
from sqlmodel import Session, select
from ..models.todo import Todo
from ..core.database import get_session


# -------------------------
# CREATE TASK
# -------------------------
def create_task(context_variables, title, description=None):
    """Create a new task for the authenticated user.

    Args:
        context_variables: Dict containing user_id
        title: Task title (required)
        description: Task description (optional)

    Returns:
        JSON string with success status and task data
    """
    user_id = context_variables.get("user_id")

    if not user_id:
        return json.dumps({
            "success": False,
            "message": "User not authenticated"
        })

    if not title or not title.strip():
        return json.dumps({
            "success": False,
            "message": "Title cannot be empty"
        })

    # Create own database session
    session = next(get_session())

    try:
        todo = Todo(
            title=title.strip(),
            description=description.strip() if description else None,
            user_id=user_id,
            is_completed=False,
        )

        session.add(todo)
        session.commit()
        session.refresh(todo)

        return json.dumps({
            "success": True,
            "message": "Task created successfully",
            "data": {
                "task_id": todo.id,
                "title": todo.title
            }
        })

    except Exception as e:
        session.rollback()
        print("create_task error:", e)
        return json.dumps({
            "success": False,
            "message": "Database error"
        })
    finally:
        session.close()


# -------------------------
# LIST TASKS
# -------------------------
def list_tasks(
    context_variables: Dict[str, Any],
    completed: Optional[bool] = None,
) -> str:
    """List all tasks for the authenticated user.

    Args:
        context_variables: Dict containing user_id
        completed: Optional filter for completed status

    Returns:
        JSON string with success status and list of tasks
    """
    user_id = context_variables.get("user_id")

    if not user_id:
        return json.dumps({
            "success": False,
            "message": "User not authenticated",
            "error": "USER_NOT_AUTHENTICATED"
        })

    # Create own database session
    session = next(get_session())

    try:
        query = select(Todo).where(Todo.user_id == user_id)

        if completed is not None:
            query = query.where(Todo.is_completed == completed)

        query = query.order_by(Todo.created_at.desc())
        todos = session.exec(query).all()

        tasks = [{
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "is_completed": t.is_completed,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
        } for t in todos]

        return json.dumps({
            "success": True,
            "message": f"Retrieved {len(tasks)} task(s)",
            "data": {
                "tasks": tasks,
                "total": len(tasks)
            }
        })

    except Exception as e:
        print("list_tasks error:", e)
        return json.dumps({
            "success": False,
            "message": "Failed to retrieve tasks",
            "error": "DATABASE_ERROR"
        })
    finally:
        session.close()


# -------------------------
# UPDATE TASK
# -------------------------
def update_task(
    context_variables: Dict[str, Any],
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None,
) -> str:
    """Update an existing task for the authenticated user.

    Args:
        context_variables: Dict containing user_id
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        is_completed: New completion status (optional)

    Returns:
        JSON string with success status and updated task data
    """
    user_id = context_variables.get("user_id")

    if not user_id:
        return json.dumps({
            "success": False,
            "message": "User not authenticated",
            "error": "USER_NOT_AUTHENTICATED"
        })

    if title is None and description is None and is_completed is None:
        return json.dumps({
            "success": False,
            "message": "No fields provided for update",
            "error": "VALIDATION_ERROR"
        })

    if title is not None:
        if not title.strip():
            return json.dumps({
                "success": False,
                "message": "Title cannot be empty",
                "error": "VALIDATION_ERROR"
            })
        if len(title) > 200:
            return json.dumps({
                "success": False,
                "message": "Title cannot exceed 200 characters",
                "error": "VALIDATION_ERROR"
            })

    if description is not None and len(description) > 1000:
        return json.dumps({
            "success": False,
            "message": "Description cannot exceed 1000 characters",
            "error": "VALIDATION_ERROR"
        })

    # Create own database session
    session = next(get_session())

    try:
        task = session.exec(
            select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)
        ).first()

        if not task:
            return json.dumps({
                "success": False,
                "message": "Task not found or access denied",
                "error": "TASK_NOT_FOUND"
            })

        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip() if description else None
        if is_completed is not None:
            task.is_completed = is_completed

        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "success": True,
            "message": "Task updated successfully",
            "data": {
                "task_id": task.id,
                "title": task.title,
                "is_completed": task.is_completed,
                "updated_at": task.updated_at.isoformat(),
            }
        })

    except Exception as e:
        session.rollback()
        print("update_task error:", e)
        return json.dumps({
            "success": False,
            "message": "Failed to update task",
            "error": "DATABASE_ERROR"
        })
    finally:
        session.close()


# -------------------------
# DELETE TASK
# -------------------------
def delete_task(
    context_variables: Dict[str, Any],
    task_id: int,
) -> str:
    """Delete a task for the authenticated user.

    Args:
        context_variables: Dict containing user_id
        task_id: ID of the task to delete

    Returns:
        JSON string with success status and deleted task info
    """
    user_id = context_variables.get("user_id")

    if not user_id:
        return json.dumps({
            "success": False,
            "message": "User not authenticated",
            "error": "USER_NOT_AUTHENTICATED"
        })

    # Create own database session
    session = next(get_session())

    try:
        task = session.exec(
            select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)
        ).first()

        if not task:
            return json.dumps({
                "success": False,
                "message": "Task not found or access denied",
                "error": "TASK_NOT_FOUND"
            })

        session.delete(task)
        session.commit()

        return json.dumps({
            "success": True,
            "message": "Task deleted successfully",
            "data": {
                "task_id": task_id,
                "title": task.title
            }
        })

    except Exception as e:
        session.rollback()
        print("delete_task error:", e)
        return json.dumps({
            "success": False,
            "message": "Failed to delete task",
            "error": "DATABASE_ERROR"
        })
    finally:
        session.close()
