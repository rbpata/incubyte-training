# High-Performance Task Scheduler

Async task scheduler backend built with FastAPI and async SQLAlchemy with PostgreSQL, supporting pagination, sorting, filtering, and retry tracking. Production-ready with Docker/Docker Compose, environment-based configuration, and comprehensive test coverage.

## Stack

- **FastAPI 0.116+** – Async path operations with pydantic validation
- **SQLAlchemy 2.0** – Async ORM with asyncpg driver
- **PostgreSQL 16** – Primary database for development and production
- **asyncpg** – Non-blocking PostgreSQL driver
- **Alembic** – Database migrations with async support
- **pydantic-settings** – Environment-driven configuration
- **Docker & Docker Compose** – Containerized development and production deployment
- **pytest** + `httpx` – Async API testing with TDD approach

## Features

- ✅ **Async endpoints** for CRUD operations
- ✅ **Pagination** with configurable page size (1-100)
- ✅ **Sorting** by created_at, run_at, status, priority (asc/desc)
- ✅ **Search** by title or description (case-insensitive)
- ✅ **Priority levels** (low, medium, high)
- ✅ **Retry tracking** (max_retries, retry_count)
- ✅ **Due-time validation** (run_at must be timezone-aware)
- ✅ **Status filtering** (pending, running, completed, failed)
- ✅ **Comprehensive test coverage** with 17 tests (100% TDD)

## Setup

### Prerequisites

- **Python 3.12+**
- **PostgreSQL 16+** (local development only; Docker Compose handles this if deployed)
- **uv** (fast Python dependency manager) – [Install uv](https://github.com/astral-sh/uv)

### Local Development (with PostgreSQL)

1. **Install dependencies:**
   ```bash
   uv sync --all-groups
   ```

2. **Set up PostgreSQL databases:**
   ```bash
   # macOS (assuming PostgreSQL installed via Homebrew)
   psql -U postgres -c "CREATE DATABASE task_db_dev;"
   psql -U postgres -c "CREATE DATABASE task_db_test;"
   
   # Or use the provided init-db.sql script:
   psql -U postgres -f init-db.sql
   ```

3. **Set environment variables** (`.env` defaults provided):
   ```bash
   # .env already configured for localhost PostgreSQL
   # No action needed; defaults work for local dev
   cat .env
   ```

4. **Run migrations:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start API server:**
   ```bash
   uv run uvicorn task_scheduler.main:app --reload
   ```
   Server runs on `http://127.0.0.1:8000`

6. **Run tests:**
   ```bash
   uv run pytest -v
   ```
   All 17 tests use `task_db_test` database; schema is isolated per test run.

### Docker Deployment (Recommended for Production)

1. **Start full stack:**
   ```bash
   docker compose up -d
   ```
   - PostgreSQL: `localhost:5432` (credentials: postgres/postgres)
   - FastAPI App: `http://localhost:8000`

2. **Run migrations in container:**
   ```bash
   docker compose exec app uv run alembic upgrade head
   ```

3. **View logs:**
   ```bash
   docker compose logs -f app
   ```

4. **Stop stack:**
   ```bash
   docker compose down
   ```

### Environment Configuration

Configuration is driven by environment variables via `.env` files:

- **`.env`** – Development defaults (localhost PostgreSQL)
- **`.env.development`** – Explicit development config (task_db_dev)
- **`.env.production`** – Production config (Docker service on postgres:5432)

Key variables:
- `DATABASE_URL` – PostgreSQL connection string
- `ENVIRONMENT` – development or production
- `LOG_LEVEL` – DEBUG, INFO, WARNING, ERROR
- `HOST` – Server host (0.0.0.0 for Docker, 127.0.0.1 for local)
- `PORT` – Server port (default 8000)
- `RELOAD` – Hot reload on code changes (true for dev, false for prod)

## API Endpoints

### Create Task
```http
POST /tasks
Content-Type: application/json

{
  "title": "Send weekly report",
  "description": "Generate and email report",
  "run_at": "2030-01-01T12:00:00+00:00",
  "priority": "high",
  "max_retries": 3
}
```

### List Tasks (with pagination, sorting, search, filtering)
```http
GET /tasks?page=1&size=10&sort_by=created_at&sort_order=desc&search=report&status=pending
```

**Query Parameters:**
- `page` (int, default=1): page number (≥1)
- `size` (int, default=10): items per page (1-100)
- `sort_by` (str, default="created_at"): created_at, run_at, status, priority
- `sort_order` (str, default="desc"): asc or desc
- `search` (str, optional): search title or description
- `status` (str, optional): pending, running, completed, failed

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Send weekly report",
      "description": "Generate and email report",
      "run_at": "2030-01-01T12:00:00+00:00",
      "status": "pending",
      "priority": "high",
      "max_retries": 3,
      "retry_count": 0,
      "created_at": "2026-03-24T10:30:00+00:00",
      "updated_at": "2026-03-24T10:30:00+00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

### Get Task by ID
```http
GET /tasks/{task_id}
```

### Update Task Status
```http
PATCH /tasks/{task_id}/status
Content-Type: application/json

{
  "status": "running"
}
```

### Delete Task
```http
DELETE /tasks/{task_id}
```

## Architecture

```
src/task_scheduler/
├── main.py              # FastAPI app factory & lifespan
├── database.py          # Async SQLAlchemy setup
├── models.py            # ORM models (Task, TaskStatus, TaskPriority)
├── schemas.py           # Pydantic models (TaskCreate, TaskRead, PaginatedTaskRead)
├── repository.py        # Data access layer (async queries with pagination/sorting/search)
├── service.py           # Business logic layer
└── routers/
    └── tasks.py         # API endpoints with dependency injection

tests/
├── test_tasks_api.py              # Core CRUD tests (4 tests)
└── test_tasks_api_extended.py     # Pagination, sorting, search, validation (13 tests)

alembic/
├── env.py               # Async Alembic configuration
└── versions/
    └── 001_add_tasks_table.py  # Initial schema migration
```

## Clean Code & TDD Principles

- **Single Responsibility**: Each layer has one reason to change (repository, service, router)
- **Async throughout**: All I/O operations are non-blocking
- **Pydantic validation**: Input validated at API boundary before business logic
- **Meaningful names**: Variables and functions are self-documenting
- **DRY**: Common query logic extracted to repository
- **TDD workflow**: Tests written first, then implementation
- **No magic**: Regex patterns for sort validation, timezone enforcement for run_at

## Database Migrations

Create new migration:
```bash
uv run alembic revision --autogenerate -m "migration message"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

Rollback last migration:
```bash
uv run alembic downgrade -1
```

## Running Tests

All tests:
```bash
uv run pytest -v
```

Core tests only:
```bash
uv run pytest tests/test_tasks_api.py -v
```

Feature tests only:
```bash
uv run pytest tests/test_tasks_api_extended.py -v
```

Specific test:
```bash
uv run pytest tests/test_tasks_api_extended.py::TestPagination::test_list_tasks_with_pagination -v
```

## Key Implementation Details

### Async SQLAlchemy with PostgreSQL
- **asyncpg driver** for non-blocking PostgreSQL operations
- **async_sessionmaker** for efficient connection pool management
- **Lifespan context manager** runs migrations on startup if needed
- **No custom datetime handling** – PostgreSQL `timestamp` type natively supports timezones

### Pagination & Sorting
- **Offset-based pagination** with exact total count via `func.count()`
- **Secondary sort by ID** to ensure deterministic ordering when primary sort has duplicates
- **Field validation** to prevent injection (regex pattern matching on sort_by)
- **Supports 4 sort columns**: created_at, run_at, status, priority (asc/desc)

### Search
- **Case-insensitive `ILIKE`** queries on title and description
- Supports partial pattern matching

### Validation
- **Pydantic field validators** enforce timezone awareness on `run_at` (must have tzinfo)
- `max_retries` limited via schema (0-10 range recommended)
- Priority defaults to "medium" if not provided
- Status only accepts: pending, running, completed, failed

### Dependency Injection (FastAPI Best Practice)
- Session injected via `Depends(get_db)` – never hardcoded
- Services receive session as parameter – no global state
- Easy to mock for unit tests or override for integration tests via `dependency_overrides`

### Test Isolation
- **conftest.py** centralizes pytest fixtures
- **test_database_url** environment variable or defaults to `task_db_test`
- **setup_test_db fixture** creates/drops schema before/after each test run
- **LifespanManager** ensures app startup logic runs (migrations, etc.)
- All 17 tests run in isolation with fresh schema

