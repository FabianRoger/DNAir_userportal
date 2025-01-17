FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create directory for local storage (if needed)
RUN mkdir -p local_storage

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV ENVIRONMENT=cloud
ENV BUCKET_NAME=dnair-data
ENV GOOGLE_CLOUD_PROJECT=dnair-database

# Initialize database (now using PostgreSQL)
RUN python init_db.py

# Start application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT