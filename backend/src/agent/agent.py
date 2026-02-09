"""AI Agent initialization and configuration.

This module sets up the OpenAI Agents SDK (Swarm) client and configures
the agent with MCP tools for task management.
"""
from typing import Dict, List, Any, Optional
from swarm import Swarm, Agent
from openai import OpenAI
from .prompts import SYSTEM_PROMPT
from .tools import create_task, list_tasks, update_task, delete_task
from ..core.config import settings


# Lazy-initialized Swarm client
_client: Optional[Swarm] = None


def get_client() -> Swarm:
    """Get or create the Swarm client with OpenAI API key from settings.

    Returns:
        Swarm: Initialized Swarm client
    """
    global _client
    if _client is None:
        # Initialize OpenAI client with API key from settings
        openai_client = OpenAI(api_key=settings.openai_api_key)
        _client = Swarm(client=openai_client)
    return _client


def get_agent() -> Agent:
    """Get the configured todo management agent.

    Returns:
        Agent: Configured agent with MCP tools and system instructions
    """
    return Agent(
        name="Todo Assistant",
        instructions=SYSTEM_PROMPT,
        functions=[
            create_task,
            list_tasks,
            update_task,
            delete_task,
        ],
    )


def invoke_agent(
    messages: List[Dict[str, Any]],
    user_id: int,
    # session: Any,  <- remove session from here
) -> Dict[str, Any]:
    """Invoke the agent with conversation context."""
    agent = get_agent()
    client = get_client()

    # Only pass serializable data
    context_variables = {
        "user_id": user_id,
        # don't pass session here
    }

    try:
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables,
        )

        return {
            "messages": response.messages,
            "agent": response.agent,
            "context_variables": response.context_variables,
        }
    except Exception as e:
        print(f"Agent invocation error: {str(e)}")
        raise
