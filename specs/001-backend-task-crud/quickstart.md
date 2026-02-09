# Quickstart Guide: Backend Core & Data Layer

**Feature**: 001-backend-task-crud
**Date**: 2026-02-08

## Overview

This guide provides step-by-step instructions for setting up and running the task management backend API locally.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless PostgreSQL account)
- Git
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd phase
git checkout 001-backend-task-crud
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

**requirements.txt**:
```
fastapi>=0.104.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
alembic>=1.13.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
```

**requirements-dev.txt**:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
pytest-cov>=4.1.0
black>=23.11.0
ruff>=0.1.6
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ENVIRONMENT=development
DEBUG=true
```

**Getting Neon Database URL**:
1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string from the dashboard
4. Replace the placeholder in `.env`

### 5. Initialize Database

```bash
# Create database tables using Alembic
alembic upgrade head

# Or for development, tables can be auto-created on startup
# (configured in backend/src/main.py)
```

## Running the Application

### Development Server

```bash
# Start FastAPI development server with auto-reload
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API Base: http://localhost:8000/api/v1
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Production Server

```bash
# Start with multiple workers
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py          # Pydantic request/response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Shared dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py     # Task CRUD endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   └── exceptions/
│       ├── __init__.py
│       └── handlers.py      # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_tasks.py        # Task endpoint tests
│   └── unit/
│       └── test_task_service.py
├── alembic/
│   ├── versions/            # Database migrations
│   └── env.py               # Alembic configuration
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md
```

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Create a Task

```bash
curl -X POST http://localhost:8000/api/v1/users/user-123/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  }'
```

Response (201 Created):
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-08T10:30:00Z",
  "updated_at": "2026-02-08T10:30:00Z"
}
```

### List Tasks

```bash
curl http://localhost:8000/api/v1/users/user-123/tasks?page=1&page_size=20 \
  -H "Authorization: Bearer <jwt-token>"
```

Response (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user-123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-08T10:30:00Z",
      "updated_at": "2026-02-08T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Get Specific Task

```bash
curl http://localhost:8000/api/v1/users/user-123/tasks/1 \
  -H "Authorization: Bearer <jwt-token>"
```

### Update Task

```bash
curl -X PATCH http://localhost:8000/api/v1/users/user-123/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "completed": true
  }'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/v1/users/user-123/tasks/1 \
  -H "Authorization: Bearer <jwt-token>"
```

Response: 204 No Content

## Testing

### Run All Tests

```bash
# Run all tests with coverage
pytest --cov=backend/src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_tasks.py

# Run with verbose output
pytest -v

# Run only integration tests
pytest tests/integration/
```

### Test Database Setup

Create a separate test database in Neon:

```bash
# .env.test
TEST_DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/test_db?sslmode=require
```

Tests automatically create and drop tables for each test using fixtures.

## Database Migrations

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to tasks"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/src/`

### 2. Format Code

```bash
# Format with black
black backend/

# Lint with ruff
ruff check backend/
```

### 3. Run Tests

```bash
pytest
```

### 4. Test Manually

Use the interactive API docs at http://localhost:8000/docs

### 5. Create Migration (if models changed)

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

**Problem**: `could not connect to server`

**Solution**:
- Verify DATABASE_URL in `.env` is correct
- Check Neon dashboard for database status
- Ensure `sslmode=require` is in connection string
- Check firewall/network settings

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Ensure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

### Migration Conflicts

**Problem**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solution**:
```bash
# Check current version
alembic current

# View pending migrations
alembic history

# Apply all pending migrations
alembic upgrade head
```

### Port Already in Use

**Problem**: `[Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn backend.src.main:app --reload --port 8001
```

## Environment-Specific Configuration

### Development

```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://...neon.tech/dev_db
```

### Testing

```bash
ENVIRONMENT=testing
DEBUG=true
DATABASE_URL=postgresql://...neon.tech/test_db
```

### Production

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://...neon.tech/prod_db
JWT_SECRET_KEY=<strong-random-key>
```

## Next Steps

1. **Implement Authentication (Spec-2)**: Add JWT token validation
2. **Build Frontend (Spec-3)**: Create Next.js UI
3. **Add Features**: Implement task priorities, tags, due dates
4. **Deploy**: Set up production deployment (Vercel, Railway, etc.)

## Useful Commands Reference

```bash
# Start development server
uvicorn backend.src.main:app --reload

# Run tests with coverage
pytest --cov=backend/src --cov-report=html

# Format code
black backend/

# Lint code
ruff check backend/

# Create migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head

# View API docs
open http://localhost:8000/docs
```

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Neon Documentation: https://neon.tech/docs/
- Alembic Documentation: https://alembic.sqlalchemy.org/
- Pytest Documentation: https://docs.pytest.org/
