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

# Install only dependencies first (cached layer)
# Using bind mounts to avoid copying unnecessary files
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project

# Copy the application code
COPY . /src
WORKDIR /src

# Install the application itself (separate layer for better caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --locked \
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

# Copy application code (only the agent directory since that's where your app is)
COPY --chown=app:app . /app/agent

# Switch to non-root user
USER app
WORKDIR /app

# Healthcheck (optional but recommended)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run the application as a module from the agent directory
CMD ["python", "-m", "agent.app"]