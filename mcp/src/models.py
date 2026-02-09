"""Task model for MCP Server.

This module imports the Task model from the backend to ensure
consistency and avoid schema duplication.
"""

import sys
from pathlib import Path

# Add backend to Python path to import Task model
backend_path = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

# Import Task model from backend
from models.task import Task

# Re-export for convenience
__all__ = ["Task"]
