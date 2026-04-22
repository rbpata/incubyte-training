# Task Scheduler Backend

A clean and practical backend for scheduling tasks with FastAPI.

## Overview

This service lets you create tasks, manage status updates, search and filter lists, and process tasks in the background.
con
## Key Features

- Async API with FastAPI
- Pagination, filtering, search, and sorting
- Retry-aware background processing
- Soft delete support
- Strong test coverage with unit and integration tests

## Architecture

High-level flow:

```text
Client Request
	|
	v
API Layer (FastAPI routes)
	|
	v
Service Layer (business rules)
	|
	v
Repository Layer (data access)
	|
	v
Database

Background jobs use the same service/repository flow for task processing.
```

Design intent:

- Keep route handlers thin
- Keep business logic centralized
- Keep database concerns isolated

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- pytest ecosystem (pytest-asyncio, pytest-cov, Hypothesis)
- testcontainers (optional)
- mutmut

## Quick Start

1. Install dependencies

```bash
uv sync --all-groups
```

2. Start the API

```bash
uv run uvicorn app.main:app --reload
```

3. Open API docs

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/openapi.json

## Database

Apply migrations:

```bash
uv run alembic upgrade head
```

Create migration:

```bash
uv run alembic revision --autogenerate -m "describe_change"
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

## API Summary

- Create task: `POST /tasks`
- List tasks: `GET /tasks`
- Get task: `GET /tasks/{task_id}`
- Update task status: `PATCH /tasks/{task_id}/status`
- Delete task: `DELETE /tasks/{task_id}`
- Process task: `POST /tasks/{task_id}/process`

Example list query:

```http
GET /tasks?page=1&size=10&sort_by=created_at&sort_order=desc&search=report&status=pending
```

## Testing

Run all tests:

```bash
.venv/bin/python -m pytest -q
```

Run with coverage target:

```bash
.venv/bin/python -m pytest --cov=src/app --cov-report=term-missing --cov-fail-under=95
```

Run only unit tests:

```bash
.venv/bin/python -m pytest tests/unit -q
```

Run only integration tests:

```bash
.venv/bin/python -m pytest tests/integration -q
```

Run mutation tests:

```bash
.venv/bin/python -m mutmut run
.venv/bin/python -m mutmut results
```

## Configuration

Common environment variables:

- DATABASE_URL
- TEST_DATABASE_URL
- ENVIRONMENT
- LOG_LEVEL
- HOST
- PORT
- RELOAD

## Notes

- Container-based tests are skip-safe when Docker is unavailable.
- The FastAPI app object is loaded from `app.main:app`.
