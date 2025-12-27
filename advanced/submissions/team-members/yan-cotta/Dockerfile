# =============================================================================
# FinResearch AI - Production Dockerfile (Full-Stack Monolith)
# Multi-Agent Financial Research System with React UI
# =============================================================================
#
# Build:
#   docker build -t finresearch-ai:latest .
#
# Run (Web Server):
#   docker run --rm -p 8000:8000 \
#     -e OPENAI_API_KEY=sk-your-key \
#     -v $(pwd)/outputs:/app/outputs \
#     finresearch-ai:latest
#
# Run (CLI Mode):
#   docker run --rm -it \
#     -e OPENAI_API_KEY=sk-your-key \
#     finresearch-ai:latest cli AAPL --sequential
#
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Frontend Builder (Node.js)
# Build the React application with Vite
# -----------------------------------------------------------------------------
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source
COPY frontend/ ./

# Build the production bundle
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Python Dependencies Builder
# Install Python dependencies in a separate stage
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS python-builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION="1.8.4" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml ./

# Generate requirements and install dependencies
RUN poetry export -f requirements.txt --without-hashes --only main > requirements.txt \
    && pip install --target=/app/deps -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 3: Production Runtime
# Minimal image with Python backend serving React frontend
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Labels for container metadata
LABEL maintainer="Yan Cotta <yan.cotta@example.com>" \
      version="1.0.0" \
      description="FinResearch AI - Multi-Agent Financial Research System" \
      org.opencontainers.image.source="https://github.com/org/finresearch-ai"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # Application paths
    APP_HOME=/app \
    PYTHONPATH=/app/deps:/app \
    # Disable telemetry
    ANONYMIZED_TELEMETRY=false \
    # ChromaDB settings
    CHROMA_PERSIST_DIR=/app/.chroma_db \
    # Default output directory
    OUTPUT_DIR=/app/outputs \
    # Server settings
    PORT=8000 \
    HOST=0.0.0.0

# Create non-root user for security
RUN groupadd --gid 1000 finresearch \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home finresearch

# Set working directory
WORKDIR ${APP_HOME}

# Copy Python dependencies from builder stage
COPY --from=python-builder /app/deps /app/deps

# Copy application code
COPY --chown=finresearch:finresearch src/ ./src/
COPY --chown=finresearch:finresearch main.py ./

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder --chown=finresearch:finresearch /app/frontend/dist ./frontend/dist

# Create directories for persistence with correct permissions
RUN mkdir -p ${OUTPUT_DIR} ${CHROMA_PERSIST_DIR} \
    && chown -R finresearch:finresearch ${APP_HOME}

# Switch to non-root user
USER finresearch

# Health check - check the API endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Volume mounts for persistent data
VOLUME ["/app/outputs", "/app/.chroma_db"]

# Expose the web server port
EXPOSE 8000

# Entry point script to support both web and CLI modes
COPY --chown=finresearch:finresearch <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

if [ "$1" = "cli" ]; then
    # CLI mode - pass remaining args to main.py
    shift
    exec python main.py "$@"
elif [ "$1" = "web" ] || [ -z "$1" ]; then
    # Web server mode (default)
    exec python -m uvicorn src.api:app --host ${HOST} --port ${PORT}
else
    # Unknown command - assume it's for the CLI
    exec python main.py "$@"
fi
EOF

# Make entrypoint executable
USER root
RUN chmod +x /app/entrypoint.sh
USER finresearch

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]

# Default command - start web server
CMD ["web"]
