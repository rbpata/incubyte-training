# API Gateway

Thin reverse-proxy that routes all client traffic to the correct downstream service.

| Path prefix         | Routed to                        |
|---------------------|----------------------------------|
| `/api/v1/auth/**`   | `auth-service` (port 8001)       |
| `/api/v1/tasks/**`  | `task-service` (port 8002)       |

The gateway also:
- Applies CORS headers once (so downstream services don't need to add them again when called via the gateway)
- Strips the `server` response header
- Forwards all request headers (including `Authorization`) unchanged

## Running locally
```bash
uv sync
uv run uvicorn main:app --reload --port 8000
```

Set `AUTH_SERVICE_URL` and `TASK_SERVICE_URL` env vars to override the defaults.
