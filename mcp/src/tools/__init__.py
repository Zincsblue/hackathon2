"""MCP tool registry and registration helpers.

This module provides the tool registry for managing MCP tool registration
and discovery.
"""

from typing import Dict, List, Callable, Any

# Global tool registry
_tool_registry: Dict[str, Callable] = {}


def register_tool(name: str, func: Callable) -> None:
    """Register an MCP tool.

    Args:
        name: Tool name (e.g., "add_task")
        func: Tool implementation function
    """
    _tool_registry[name] = func
    print(f"[INFO] Registered tool: {name}")


def get_tool(name: str) -> Callable:
    """Get a registered tool by name.

    Args:
        name: Tool name

    Returns:
        Tool implementation function

    Raises:
        KeyError: If tool not found
    """
    return _tool_registry[name]


def list_tools() -> List[str]:
    """List all registered tool names.

    Returns:
        List of tool names
    """
    return list(_tool_registry.keys())


def get_tool_count() -> int:
    """Get the number of registered tools.

    Returns:
        Number of registered tools
    """
    return len(_tool_registry)


# Tool registry will be populated by importing tool modules
__all__ = ["register_tool", "get_tool", "list_tools", "get_tool_count"]
