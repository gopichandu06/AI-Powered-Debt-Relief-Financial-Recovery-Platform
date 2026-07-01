FROM python:3.11-slim

LABEL maintainer="FinRelief AI Team"
LABEL description="FinRelief AI FastAPI Backend"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Environment defaults (override via docker run -e or docker-compose)
ENV DATABASE_URL=sqlite:///./data/finrelief.db
ENV APP_NAME="FinRelief AI"
ENV APP_VERSION="1.0.0"
ENV DEBUG=false

# Expose the application port
EXPOSE 8000

# Start uvicorn with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
