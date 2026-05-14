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

# Copy all application code (needed for pip install .)
COPY . .

# Install Python dependencies using the new pyproject.toml
RUN pip install --no-cache-dir .

# Create data directory and initialize database
RUN mkdir -p data && python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/agent_audit.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        topic TEXT,
        action TEXT,
        status TEXT,
        url TEXT
    )
''')
conn.commit()
conn.close()
EOF

# Keep the container running interactively
CMD ["python3", "main.py"]
