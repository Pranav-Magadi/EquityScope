# EquityScope Backend - Multi-stage Docker Build
# Optimized for both development and production deployments

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy source code
COPY . .

# Create directories
RUN mkdir -p /app/data /app/cache /app/logs

# Expose port
EXPOSE 8000

# Development command (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r equityscope && useradd -r -g equityscope equityscope

# Copy only necessary files
COPY app/ ./app/
COPY start_server.py ./

# Create directories and set permissions
RUN mkdir -p /app/data /app/cache /app/logs && \
    chown -R equityscope:equityscope /app

# Switch to non-root user
USER equityscope

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["python", "start_server.py"]