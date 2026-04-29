# Detect OS for cross-platform compatibility
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := pip
else
    PYTHON := python3
    PIP := pip3
endif

.PHONY: setup run test lint clean docker-build docker-run docker-test

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -e ".[dev]"

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy .

audit:
	sqlite3 agent_audit.db "SELECT timestamp, topic, status FROM audit_logs ORDER BY timestamp DESC LIMIT 10;"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker compose build

docker-run:
	docker compose run --rm agent

docker-test:
	docker compose run --rm agent python3 -m pytest tests/
