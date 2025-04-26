# syntax=docker/dockerfile:1.9
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Use bash shell with pipefail option for better error detection
SHELL ["sh", "-exc"]

# Set environment variables for uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
    UV_PROJECT_ENVIRONMENT=/app

# Copy pyproject.toml for dependency resolution
COPY pyproject.toml /tmp/pyproject.toml

# Install dependencies first (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    cd /tmp && \
    uv sync \
        --python ${UV_PYTHON} \
        --project /tmp \
        --no-dev

# Copy the application code
COPY . /src
WORKDIR /src

# Install the application itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --python ${UV_PYTHON} \
        --no-dev \
        --no-editable

##########################################################################

# Production stage - only runtime dependencies
FROM python:3.11-slim-bookworm

SHELL ["sh", "-exc"]

# Add virtualenv to PATH
ENV PATH=/app/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd -r app && \
    useradd -r -d /app -g app app

# Copy the pre-built virtualenv from builder
COPY --from=builder --chown=app:app /app /app

# Copy application code
COPY --chown=app:app . /app

# Switch to non-root user
USER app
WORKDIR /app

# Install curl for healthcheck
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
USER app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Expose the ports
EXPOSE 9090
EXPOSE 3000

# Run the metrics server
CMD ["python", "metrics_server.py"]
