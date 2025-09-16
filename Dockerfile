# Multi-stage build for ISA SuperApp
FROM python:3.11-slim as builder

# Set build arguments
ARG POETRY_VERSION=1.7.1
ARG POETRY_HOME=/opt/poetry
ARG POETRY_VENV=/opt/poetry-venv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry in isolated virtual environment
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==$POETRY_VERSION

# Add Poetry to PATH
ENV PATH="${POETRY_VENV}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Production stage with distroless for minimal attack surface
FROM gcr.io/distroless/python3-debian11:nonroot as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:$PATH"

# Copy installed packages from builder stage
COPY --from=builder --chown=nonroot:nonroot /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder --chown=nonroot:nonroot /usr/local/bin /usr/local/bin

# Copy application code with minimal permissions
COPY --chown=nonroot:nonroot . /app

# Set working directory
WORKDIR /app

# Create necessary directories with proper ownership
RUN mkdir -p /app/logs /app/data /app/static /app/media

# Switch to non-root user (distroless nonroot uid=65532)
USER 65532:65532

# Expose port
EXPOSE 8000

# Health check with proper command for distroless
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["/usr/bin/python3", "-c", "import requests; requests.get('http://localhost:8000/health')"]

# Run the application with optimized settings for ISA workloads
CMD ["/usr/bin/python3", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "-", "--error-logfile", "-", "isa_superapp.main:app"]