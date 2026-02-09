# Quickstart Guide: MCP Server & Task Tools

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Status**: Complete

## Overview

This guide helps you get started with the MCP server for task management. The MCP server exposes five stateless tools that AI agents can use to manage tasks through the MCP protocol.

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database (from Spec-1)
- Existing Task schema and User authentication (from Spec-1 and Spec-2)
- Official MCP SDK installed

## Installation

### 1. Install Dependencies

```bash
cd mcp
pip install -r requirements.txt
```

**requirements.txt**:
```
mcp>=1.0.0
sqlmodel==0.0.22
psycopg2-binary==2.9.9
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### 2. Configure Environment

Create `.env` file in `mcp/` directory:

```bash
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
MCP_SERVER_PORT=8002
LOG_LEVEL=INFO
```

## Starting the MCP Server

### Development Mode

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

### Production Mode

```bash
cd mcp
python src/server.py --production
```

## Using MCP Tools

### Tool Invocation Examples

**Note**: These examples show the JSON payloads. Actual invocation depends on your MCP client implementation.

#### 1. Create a Task

```json
{
  "tool": "add_task",
  "parameters": {
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 10,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T10:30:00Z"
  }
}
```

#### 2. List All Tasks

```json
{
  "tool": "list_tasks",
  "parameters": {
    "user_id": 1
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 10,
        "user_id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2026-02-09T10:30:00Z",
        "updated_at": "2026-02-09T10:30:00Z"
      }
    ],
    "count": 1
  }
}
```

#### 3. Complete a Task

```json
{
  "tool": "complete_task",
  "parameters": {
    "user_id": 1,
    "task_id": 10
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 10,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T11:00:00Z"
  }
}
```

#### 4. Update a Task

```json
{
  "tool": "update_task",
  "parameters": {
    "user_id": 1,
    "task_id": 10,
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, chicken"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 10,
    "user_id": 1,
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, chicken",
    "completed": true,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T11:15:00Z"
  }
}
```

#### 5. Delete a Task

```json
{
  "tool": "delete_task",
  "parameters": {
    "user_id": 1,
    "task_id": 10
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "task_id": 10,
    "message": "Task successfully deleted"
  }
}
```

## Verifying Tool Functionality

### Manual Testing

Use the MCP client or test script to verify each tool:

```bash
cd mcp/tests
python test_tools.py
```

Expected output:
```
test_add_task ... PASS
test_list_tasks ... PASS
test_complete_task ... PASS
test_update_task ... PASS
test_delete_task ... PASS
test_user_isolation ... PASS
test_error_handling ... PASS

All tests passed (7/7)
```

### Database Verification

Check that tasks are persisted correctly:

```sql
-- Connect to Neon database
psql $DATABASE_URL

-- View tasks for user
SELECT * FROM tasks WHERE user_id = 1;

-- Verify user isolation
SELECT user_id, COUNT(*) FROM tasks GROUP BY user_id;
```

## Integration with AI Agents (Spec-5 Preview)

### Agent Configuration

AI agents can discover and invoke MCP tools:

```python
# Example: AI agent using MCP tools
from mcp_client import MCPClient

client = MCPClient("http://localhost:8002")

# Discover available tools
tools = client.list_tools()
print(tools)  # ['add_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task']

# Invoke tool
result = client.invoke_tool("add_task", {
    "user_id": 1,
    "title": "Review pull request",
    "description": "Check code quality and tests"
})

print(result)
```

### Agent Workflow Example

```
User: "Add a task to buy groceries"
  ↓
AI Agent: Invokes add_task tool
  ↓
MCP Server: Creates task in database
  ↓
AI Agent: Confirms task created
  ↓
User: "Task added successfully!"
```

## Troubleshooting

### Server Won't Start

**Problem**: `Database connection failed`

**Solution**:
1. Verify DATABASE_URL in .env file
2. Check Neon database is accessible
3. Verify network connectivity

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Tool Invocation Fails

**Problem**: `USER_NOT_FOUND` error

**Solution**:
1. Verify user_id exists in users table
2. Check user was created via Spec-2 authentication

```sql
SELECT id, email FROM users WHERE id = 1;
```

**Problem**: `UNAUTHORIZED` error

**Solution**:
1. Verify user_id matches task owner
2. Check task_id is correct

```sql
SELECT id, user_id, title FROM tasks WHERE id = 10;
```

### Performance Issues

**Problem**: Tool invocations taking >2 seconds

**Solution**:
1. Check database connection pool size
2. Verify database indexes exist
3. Monitor database query performance

```bash
# Check connection pool
grep "pool_size" mcp/src/database.py

# Verify indexes
psql $DATABASE_URL -c "\d tasks"
```

## Monitoring

### Server Logs

Logs are written to `mcp/logs/server.log`:

```bash
tail -f mcp/logs/server.log
```

Log format:
```
[2026-02-09 10:30:00] [INFO] Tool invoked: add_task, user_id=1, result=success
[2026-02-09 10:30:15] [INFO] Tool invoked: list_tasks, user_id=1, result=success, count=1
[2026-02-09 10:30:30] [ERROR] Tool invoked: complete_task, user_id=1, task_id=999, result=error, code=TASK_NOT_FOUND
```

### Health Check

```bash
# Check if server is running
curl http://localhost:8002/health

# Expected response
{"status": "healthy", "tools": 5, "database": "connected"}
```

## Next Steps

1. ✅ MCP server running and tools accessible
2. ⬜ Integrate with AI agent (Spec-5)
3. ⬜ Deploy to production environment
4. ⬜ Set up monitoring and alerting
5. ⬜ Configure backup and disaster recovery

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
- [Official MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)

## Support

For issues or questions:
1. Check server logs: `mcp/logs/server.log`
2. Review tool contracts: `specs/004-mcp-task-tools/contracts/mcp-tools.md`
3. Verify database connectivity
4. Check MCP SDK version compatibility
