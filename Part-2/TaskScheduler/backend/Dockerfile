# Multi-stage backend build for minimal final image
FROM python:3.12-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY services/api-gateway/pyproject.toml services/api-gateway/uv.lock ./
RUN uv sync --frozen

# Repeat for other services (for monorepo structure)
# This assumes services might be deployed separately or via multi-service compose


# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy minimal runtime dependencies from builder
COPY --from=builder /root/.cache/uv /root/.cache/uv
COPY --from=builder /app /app

RUN pip install --no-cache-dir uv

# Copy source code (not cached in builder for flexibility)
COPY services/api-gateway/main.py ./main.py
COPY services/api-gateway/src/ ./src/
COPY services/api-gateway/README.md ./README.md

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
