# Detect OS for cross-platform compatibility
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := pip
else
    PYTHON := python3
    PIP := pip3
endif

.PHONY: setup run test lint clean docker-build docker-run

setup:
	$(PIP) install -e ".[dev]"

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker compose build

docker-run:
	docker compose run --rm agent
