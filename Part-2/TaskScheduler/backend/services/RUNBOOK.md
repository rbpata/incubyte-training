# Observability Runbook — Task Scheduler

## Architecture

```
Services ──► /metrics (Prometheus scrape)
         ──► stdout JSON logs (log aggregator)
         ──► Sentry (error tracking, optional)

Prometheus ──► Grafana (dashboards + alerting)
```

## Services & Ports

| Service      | Port | Health         | Metrics         |
|-------------|------|----------------|-----------------|
| auth-service | 8001 | /health/ready  | /metrics        |
| task-service | 8002 | /health/ready  | /metrics        |
| api-gateway  | 8000 | -              | -               |
| Prometheus   | 9090 | -              | -               |
| Grafana      | 3001 | -              | admin/admin     |

---

## 1. Structured JSON Logs

Every log line is JSON on stdout:

```json
{
  "timestamp": "2026-04-15T12:00:00.000Z",
  "level": "INFO",
  "service": "task-service",
  "logger": "app.core.middleware",
  "message": "http_request",
  "method": "POST",
  "path": "/api/v1/tasks",
  "status_code": 201,
  "duration_ms": 12.4,
  "correlation_id": "abc-123"
}
```

### Log Aggregation (Docker)
```bash
# tail all service logs
docker compose logs -f auth-service task-service

# filter errors only
docker compose logs --no-log-prefix task-service | grep '"level": "ERROR"'

# filter by correlation_id
docker compose logs | grep '"correlation_id": "YOUR-ID"'
```

### Log Aggregation Patterns (production)
- Ship stdout to **Loki** (Grafana stack) or **OpenSearch** via Fluentd/Vector
- Index on: `service`, `level`, `correlation_id`, `path`
- Alert on: `level = ERROR` rate > threshold

---

## 2. Prometheus Metrics

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Labels: method, path, status_code |
| `http_request_duration_seconds` | Histogram | Labels: method, path |
| `tasks_created_total` | Counter | Labels: user_id |
| `tasks_completed_total` | Counter | - |
| `tasks_failed_total` | Counter | - |
| `active_tasks_total` | Gauge | Current active tasks |
| `background_jobs_total` | Counter | Labels: result |
| `auth_login_attempts_total` | Counter | Labels: result (success/failure) |
| `auth_registrations_total` | Counter | - |
| `auth_token_refreshes_total` | Counter | Labels: result |
| `api_keys_created_total` | Counter | - |

### Useful PromQL Queries

```promql
# Request rate per second (last 1m)
rate(http_requests_total[1m])

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate %
rate(http_requests_total{status_code=~"5.."}[1m]) / rate(http_requests_total[1m]) * 100

# Login failure rate
rate(auth_login_attempts_total{result="failure"}[5m])

# Task creation rate
rate(tasks_created_total[5m])
```

---

## 3. Grafana Dashboard

Access: http://localhost:3001 (admin/admin)

Dashboard: **TaskScheduler → Task Scheduler - Observability**

Panels:
- HTTP Request Rate (timeseries)
- HTTP P95 Latency (timeseries)
- Tasks Created/min (stat)
- Login Success Rate (stat)
- Active Tasks (stat)
- Background Job Results (piechart)
- HTTP Error Rate 4xx/5xx (timeseries)

### Alerting Rules (recommended)

```yaml
# Add to prometheus/alerts.yml and reference from prometheus.yml
groups:
  - name: task-scheduler
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High 5xx error rate on {{ $labels.job }}"

      - alert: SlowRequests
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency > 1s on {{ $labels.job }}"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.job }} is down"
```

---

## 4. Health Checks

| Endpoint | Use case |
|----------|----------|
| `GET /health` | Basic alive check |
| `GET /health/live` | Kubernetes liveness probe |
| `GET /health/ready` | Kubernetes readiness probe (checks DB) |

```bash
# manual check
curl http://localhost:8001/health/ready
curl http://localhost:8002/health/ready

# Expected 200
{"status": "ready", "service": "auth-service", "db": "ok"}

# If DB is down: 503
{"detail": "DB unavailable: ..."}
```

---

## 5. Sentry Error Tracking

Set `SENTRY_DSN` env var to enable. Leave unset to disable (no-op).

```bash
# docker-compose environment section
SENTRY_DSN: "https://xxx@sentry.io/yyy"
```

### Triage workflow
1. Sentry alert fires → open issue in Sentry UI
2. Check **stack trace** + **breadcrumbs**
3. Find `correlation_id` in Sentry extra context
4. Search logs: `grep '"correlation_id": "VALUE"' logs`
5. Check Grafana for spike at timestamp
6. Fix → deploy → mark resolved in Sentry

---

## 6. Runbook: Incident Response

### Service not responding
1. `curl /health/live` → if 503, service crashed → check `docker compose logs`
2. `curl /health/ready` → if 503, DB issue → check postgres health
3. Restart: `docker compose restart <service>`

### Elevated error rate
1. Grafana: check HTTP Error Rate panel
2. PromQL: `rate(http_requests_total{status_code=~"5.."}[1m])`
3. Find bad endpoints → check application logs for those paths
4. Check Sentry for new error groups

### High latency
1. Grafana: check P95 Latency panel
2. PromQL: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
3. Identify slow paths → check DB query logs (set `LOG_LEVEL=DEBUG`)

### DB connection exhaustion
1. `curl /health/ready` → 503 = DB unreachable
2. Check postgres: `docker compose logs postgres`
3. Check active connections: `SELECT count(*) FROM pg_stat_activity;`
