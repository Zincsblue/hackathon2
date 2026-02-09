"""
MCP Client for invoking MCP tools from the backend.

This module implements the MCPClient which wraps HTTP calls to the MCP server
and provides methods for all 5 task management tools.
"""

import requests
from typing import Dict, Any, Optional
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MCPClient:
    """
    Client for invoking MCP tools via HTTP requests.

    This client wraps the MCP server API and provides methods for:
    - add_task: Create a new task
    - list_tasks: Retrieve user's tasks
    - complete_task: Mark a task as completed
    - update_task: Update task details
    - delete_task: Permanently remove a task
    """

    def __init__(self, mcp_server_url: Optional[str] = None):
        """
        Initialize MCP client with retry logic.

        Args:
            mcp_server_url: Base URL of the MCP server (defaults to env var)
        """
        self.base_url = mcp_server_url or os.getenv("MCP_SERVER_URL", "http://localhost:8001")

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,  # Maximum number of retries
            backoff_factor=0.5,  # Wait 0.5, 1.0, 2.0 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["POST"]  # Only retry POST requests
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def add_task(self, user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task for the user.

        Args:
            user_id: User identifier
            title: Task title
            description: Optional task description

        Returns:
            Dictionary with task details or error
        """
        try:
            response = requests.post(
                f"{self.base_url}/tools/add_task",
                json={
                    "user_id": user_id,
                    "title": title,
                    "description": description
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "MCP_TOOL_ERROR",
                "message": f"Failed to create task: {str(e)}"
            }

    def list_tasks(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all tasks for the user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with list of tasks or error
        """
        try:
            response = requests.post(
                f"{self.base_url}/tools/list_tasks",
                json={"user_id": user_id},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "MCP_TOOL_ERROR",
                "message": f"Failed to list tasks: {str(e)}"
            }

    def complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Dictionary with updated task or error
        """
        try:
            response = requests.post(
                f"{self.base_url}/tools/complete_task",
                json={
                    "user_id": user_id,
                    "task_id": task_id
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "MCP_TOOL_ERROR",
                "message": f"Failed to complete task: {str(e)}"
            }

    def update_task(
        self,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task details.

        Args:
            user_id: User identifier
            task_id: Task identifier
            title: Optional new title
            description: Optional new description

        Returns:
            Dictionary with updated task or error
        """
        try:
            payload = {"user_id": user_id, "task_id": task_id}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description

            response = requests.post(
                f"{self.base_url}/tools/update_task",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "MCP_TOOL_ERROR",
                "message": f"Failed to update task: {str(e)}"
            }

    def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Permanently delete a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Dictionary with success status or error
        """
        try:
            response = requests.post(
                f"{self.base_url}/tools/delete_task",
                json={
                    "user_id": user_id,
                    "task_id": task_id
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "MCP_TOOL_ERROR",
                "message": f"Failed to delete task: {str(e)}"
            }
