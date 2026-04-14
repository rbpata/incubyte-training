# Task Service

Microservice responsible for task CRUD operations and background task processing.

## Responsibilities
- Create, list, read, update status, and soft-delete tasks
- Background processing of tasks (retry logic included)

## Authentication
JWT tokens are validated **locally** using the shared `SECRET_KEY`.  
No network call to the auth-service is required; the JWT contains the `user_id` and `role`.

## Endpoints
- `POST   /api/v1/tasks`
- `GET    /api/v1/tasks`
- `GET    /api/v1/tasks/{id}`
- `PATCH  /api/v1/tasks/{id}/status`
- `DELETE /api/v1/tasks/{id}`
- `POST   /api/v1/tasks/{id}/process`

## Running locally
```bash
uv sync
uv run uvicorn main:app --reload --port 8002
```
