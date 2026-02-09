# MCP Server - Task Management Tools

A stateless MCP (Model Context Protocol) server that exposes task management operations as tools for AI agents.

## Overview

This MCP server provides five stateless tools for managing tasks:
- `add_task` - Create a new task
- `list_tasks` - Retrieve all tasks for a user
- `complete_task` - Mark a task as completed
- `update_task` - Modify task details
- `delete_task` - Permanently remove a task

All tools are database-backed and enforce user isolation. The server maintains zero in-memory state between invocations.

## Features

- **Stateless Architecture**: No session state, all data persists in PostgreSQL
- **User Isolation**: Every operation is scoped to a specific user_id
- **Structured Responses**: Consistent JSON format for success and error cases
- **Database-Backed**: Direct integration with Neon Serverless PostgreSQL
- **Audit Logging**: All tool invocations are logged with user_id and outcome

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database (from Spec-1)
- Existing Task schema and User authentication (from Spec-1 and Spec-2)

## Installation

1. Install dependencies:
```bash
cd mcp
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Verify database connection:
```bash
python -c "from src.database import get_engine; get_engine()"
```

## Usage

### Starting the MCP Server

```bash
cd mcp
python src/server.py
```

Expected output:
```
[INFO] MCP Server starting...
[INFO] Database connection established
[INFO] Registered 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
[INFO] MCP Server listening on port 8002
[INFO] Server ready for tool invocations
```

### Tool Invocation Examples

See [quickstart.md](../specs/004-mcp-task-tools/quickstart.md) for detailed examples of invoking each tool.

## Architecture

- **Server**: `src/server.py` - MCP server initialization and lifecycle
- **Database**: `src/database.py` - Connection pool and session management
- **Models**: `src/models.py` - Task model (imported from backend)
- **Schemas**: `src/schemas.py` - Tool input/output validation
- **Tools**: `src/tools/*.py` - Individual tool implementations

## Testing

Run the test suite:
```bash
cd mcp
pytest tests/ -v
```

Run specific test suites:
```bash
pytest tests/test_add_task.py -v
pytest tests/test_user_isolation.py -v
pytest tests/test_concurrency.py -v
```

## Development

### Adding a New Tool

1. Create tool file in `src/tools/`
2. Define input/output schemas in `src/schemas.py`
3. Implement tool with `@mcp.tool()` decorator
4. Register tool in `src/server.py`
5. Add tests in `tests/`

### Code Standards

- All tools must be stateless
- All database queries must include user_id filtering
- All errors must return structured responses
- All operations must complete within 5 seconds

## Troubleshooting

See [quickstart.md](../specs/004-mcp-task-tools/quickstart.md) for common issues and solutions.

## Documentation

- [Specification](../specs/004-mcp-task-tools/spec.md)
- [Implementation Plan](../specs/004-mcp-task-tools/plan.md)
- [API Contracts](../specs/004-mcp-task-tools/contracts/mcp-tools.md)
- [Quickstart Guide](../specs/004-mcp-task-tools/quickstart.md)

## License

Part of the Todo Full-Stack Web Application hackathon project.
