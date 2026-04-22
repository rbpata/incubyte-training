from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

REGISTRY = CollectorRegistry(auto_describe=False)

# HTTP metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
    registry=REGISTRY,
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY,
)

# Business metrics
TASKS_CREATED_TOTAL = Counter(
    "tasks_created_total",
    "Total tasks created",
    ["user_id"],
    registry=REGISTRY,
)
TASKS_COMPLETED_TOTAL = Counter(
    "tasks_completed_total",
    "Total tasks completed",
    registry=REGISTRY,
)
TASKS_FAILED_TOTAL = Counter(
    "tasks_failed_total",
    "Total tasks that failed processing",
    registry=REGISTRY,
)
ACTIVE_TASKS_GAUGE = Gauge(
    "active_tasks_total",
    "Current number of active (non-completed/non-failed) tasks",
    registry=REGISTRY,
)
BACKGROUND_JOBS_TOTAL = Counter(
    "background_jobs_total",
    "Total background jobs processed",
    ["result"],
    registry=REGISTRY,
)


def get_metrics() -> tuple[bytes, str]:
    """Return Prometheus metrics in text format."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
