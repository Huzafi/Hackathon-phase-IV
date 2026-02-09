"""AI Agent module for natural language task management.

This module provides AI agent capabilities using OpenAI Agents SDK (Swarm)
with MCP tools for task operations.
"""
from .agent import get_agent, invoke_agent
from .tools import (
    create_task,
    list_tasks,
    update_task,
    delete_task,
)

__all__ = [
    "get_agent",
    "invoke_agent",
    "create_task",
    "list_tasks",
    "update_task",
    "delete_task",
]
