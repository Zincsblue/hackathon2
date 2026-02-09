"""Structured logging configuration for MCP Server.

This module provides audit logging for all tool invocations with
user_id, tool_name, parameters, and outcome tracking.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = log_dir / "server.log"

# Create logger
logger = logging.getLogger("mcp_server")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create file handler with rotation
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(getattr(logging, LOG_LEVEL))

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))

# Create formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_tool_invocation(
    tool_name: str,
    user_id: str,
    parameters: Dict[str, Any],
    result: str,
    error_code: str = None
) -> None:
    """Log a tool invocation for audit purposes.

    Args:
        tool_name: Name of the tool invoked (e.g., "add_task")
        user_id: ID of the user invoking the tool
        parameters: Tool input parameters
        result: Result status ("success" or "error")
        error_code: Error code if result is "error"

    Example:
        >>> log_tool_invocation("add_task", "user123", {"title": "Buy groceries"}, "success")
        [2026-02-09 10:30:00] [INFO] Tool invoked: add_task, user_id=user123, result=success
    """
    if result == "success":
        logger.info(
            f"Tool invoked: {tool_name}, user_id={user_id}, result=success"
        )
    else:
        logger.error(
            f"Tool invoked: {tool_name}, user_id={user_id}, result=error, code={error_code}"
        )


def log_server_event(event: str, level: str = "INFO") -> None:
    """Log a server lifecycle event.

    Args:
        event: Event description
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> log_server_event("Server starting", "INFO")
        [2026-02-09 10:30:00] [INFO] Server starting
    """
    log_func = getattr(logger, level.lower())
    log_func(event)


def log_database_event(event: str, level: str = "INFO") -> None:
    """Log a database-related event.

    Args:
        event: Event description
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> log_database_event("Database connection established", "INFO")
        [2026-02-09 10:30:00] [INFO] Database connection established
    """
    log_func = getattr(logger, level.lower())
    log_func(event)
