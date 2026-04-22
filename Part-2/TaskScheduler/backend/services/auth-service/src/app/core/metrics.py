from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

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
AUTH_LOGIN_ATTEMPTS_TOTAL = Counter(
    "auth_login_attempts_total",
    "Total login attempts",
    ["result"],  # "success" | "failure"
    registry=REGISTRY,
)
AUTH_REGISTRATIONS_TOTAL = Counter(
    "auth_registrations_total",
    "Total user registrations",
    registry=REGISTRY,
)
AUTH_TOKEN_REFRESHES_TOTAL = Counter(
    "auth_token_refreshes_total",
    "Total token refresh attempts",
    ["result"],
    registry=REGISTRY,
)
API_KEYS_CREATED_TOTAL = Counter(
    "api_keys_created_total",
    "Total API keys created",
    registry=REGISTRY,
)


def get_metrics() -> tuple[bytes, str]:
    """Return Prometheus metrics in text format."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
