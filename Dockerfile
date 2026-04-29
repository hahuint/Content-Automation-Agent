FROM python:3.11-slim

# Set environment variable to tell the code it's in Docker
ENV RUNNING_IN_DOCKER=true
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies using the new pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy all application code
COPY . .

# Keep the container running interactively
CMD ["python", "main.py"]
