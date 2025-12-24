# Multi-stage Dockerfile for optimized production build
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements-prod.txt .
# Set PATH in builder stage to avoid warnings
ENV PATH=/root/.local/bin:$PATH
RUN pip install --no-cache-dir --user --no-warn-script-location -r requirements-prod.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Explicitly ensure db_config.py is present
COPY db_config.py /app/db_config.py

# Create necessary directories
RUN mkdir -p uploads chroma_db config logs data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 6001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:6001/health || exit 1

# Run application
CMD ["python", "app.py"]

