# Auth Service

Microservice responsible for user authentication, JWT token management, and API key management.

## Responsibilities
- User registration and login
- JWT access & refresh token issuance
- Refresh token storage and revocation
- API key creation and validation

## Endpoints
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET  /api/v1/auth/me`
- `POST /api/v1/auth/api-keys`
- `GET  /api/v1/auth/api-keys`

## Running locally
```bash
uv sync
uv run uvicorn main:app --reload --port 8001
```
