# Backend Core & Data Layer - Todo Application

**Feature**: Backend task management API with user-scoped CRUD operations

**Branch**: `001-backend-task-crud`

## Overview

This is a RESTful API backend for task management built with FastAPI, SQLModel, and Neon Serverless PostgreSQL. The system enforces user-scoped data isolation and provides clean API endpoints for task CRUD operations.

## Tech Stack

- **Backend Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Migrations**: Alembic
- **Testing**: pytest with pytest-asyncio

## Prerequisites

- Python 3.11 or higher
- Neon Serverless PostgreSQL account
- Git

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd phase
git checkout 001-backend-task-crud
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Neon DATABASE_URL
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API Base: http://localhost:8000/api/v1
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/users/{user_id}/tasks` - Create task
- `GET /api/v1/users/{user_id}/tasks` - List tasks (with pagination)
- `GET /api/v1/users/{user_id}/tasks/{task_id}` - Get specific task
- `PATCH /api/v1/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` - Delete task

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/routes/      # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── exceptions/      # Custom exceptions
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI app entry
└── tests/
    ├── unit/            # Unit tests
    └── integration/     # Integration tests
```

## Development

### Run Tests

```bash
pytest --cov=backend/src --cov-report=html
```

### Format Code

```bash
black backend/
```

### Lint Code

```bash
ruff check backend/
```

### Create Migration

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Documentation

- Full specification: `specs/001-backend-task-crud/spec.md`
- Implementation plan: `specs/001-backend-task-crud/plan.md`
- API contract: `specs/001-backend-task-crud/contracts/openapi.yaml`
- Developer guide: `specs/001-backend-task-crud/quickstart.md`

## Features

- ✅ User-scoped task management
- ✅ RESTful API with JSON request/response
- ✅ Pagination and filtering support
- ✅ Proper HTTP status codes (200, 201, 204, 400, 404, 422, 500)
- ✅ Data persistence in Neon PostgreSQL
- ✅ Database migrations with Alembic
- ✅ Comprehensive error handling

## Next Steps

- **Spec-2**: Add JWT authentication and user management
- **Spec-3**: Build Next.js frontend UI

## License

[Your License Here]
