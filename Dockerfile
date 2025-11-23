# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn asyncpg psycopg2-binary httpx

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directory for SQLite db and logs
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV RAGLINT_DB_PATH="sqlite+aiosqlite:///data/raglint.db"

# Expose port
EXPOSE 8000

# Run command
CMD ["uvicorn", "raglint.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
