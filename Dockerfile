# Use a lightweight Python base
FROM python:3.10-slim

# Set environment variables to prevent .pyc files and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for better caching)
COPY pyproject.toml README.md ./

# Install dependencies
# We install the project in "editable" mode or directly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy the rest of the code
COPY . .

# Expose the port the dashboard runs on
EXPOSE 8000

# Start the dashboard when the container starts
# We use uvicorn directly for production
CMD ["uvicorn", "raglint.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
