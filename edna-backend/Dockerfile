FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory
COPY . .

# Create directory for local storage
RUN mkdir -p local_storage

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV ENVIRONMENT=cloud
ENV BUCKET_NAME=dnair-data
ENV GOOGLE_CLOUD_PROJECT=dnair-database

# Initialize database
RUN python -c "from app.models.models import Base; from app.db.database import engine; Base.metadata.create_all(bind=engine)"

# Start application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT