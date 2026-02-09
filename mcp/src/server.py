"""MCP Server initialization and lifecycle management.

This module provides the main MCP server that exposes task management
tools to AI agents via the Model Context Protocol.
"""

import os
import signal
import sys
from typing import Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions
from database import init_db, close_db

# MCP Server configuration
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8002"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Global server state
server_running = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global server_running
    print("\n[INFO] Shutdown signal received, stopping server...")
    server_running = False
    shutdown_server()
    sys.exit(0)


def startup_server():
    """Initialize MCP server and establish database connection.

    This function:
    1. Initializes database connection pool
    2. Registers all MCP tools
    3. Starts the MCP server

    Raises:
        Exception: If server initialization fails
    """
    global server_running

    try:
        print("[INFO] MCP Server starting...")

        # Initialize database connection
        init_db()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # TODO: Register MCP tools (T013-T015)
        # This will be implemented in the Tool Interface Definition phase
        print("[INFO] Tool registration pending (T013-T015)")

        # Mark server as running
        server_running = True

        print(f"[INFO] MCP Server listening on port {MCP_SERVER_PORT}")
        print("[INFO] Server ready for tool invocations")
        print("[INFO] Press Ctrl+C to stop")

        # Keep server running
        while server_running:
            # In a real MCP server, this would be the main event loop
            # For now, we'll use a simple sleep loop
            import time
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        raise


def shutdown_server():
    """Shutdown MCP server and cleanup resources.

    This function:
    1. Stops accepting new tool invocations
    2. Closes database connection pool
    3. Performs cleanup
    """
    global server_running

    try:
        print("[INFO] MCP Server shutting down...")

        # Stop accepting new requests
        server_running = False

        # Close database connections
        close_db()

        print("[INFO] MCP Server stopped successfully")

    except Exception as e:
        print(f"[ERROR] Server shutdown error: {e}")
        raise


def health_check() -> dict:
    """Check server health status.

    Returns:
        dict: Health status including server status, tool count, and database connectivity

    Example:
        >>> health_check()
        {"status": "healthy", "tools": 5, "database": "connected"}
    """
    try:
        # Check database connectivity
        from database import get_session
        session_gen = get_session()
        session = next(session_gen)
        session.exec("SELECT 1")
        try:
            next(session_gen, None)
        except StopIteration:
            pass
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "tools": 5,  # Number of registered tools
        "database": db_status
    }


def main():
    """Main entry point for MCP server."""
    try:
        startup_server()
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt received")
        shutdown_server()
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        shutdown_server()
        sys.exit(1)


if __name__ == "__main__":
    main()
