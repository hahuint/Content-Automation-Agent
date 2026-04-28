FROM python:3.11-slim

# Set environment variable to tell the code it's in Docker
ENV RUNNING_IN_DOCKER=true
ENV PYTHONUNBUFFERED=1

# Install system dependencies (Chromium and Driver for Selenium)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Keep the container running interactively
CMD ["python", "main.py"]
