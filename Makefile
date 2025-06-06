.PHONY: help install-deps run-dev test lint

help:
	@echo "Available commands:"
	@echo "  install-deps   - Install backend and frontend dependencies"
	@echo "  run-dev        - Start backend and frontend for development"
	@echo "  test           - Run backend tests"
	@echo "  lint           - Lint backend code"

install-deps:
	@echo "Installing backend dependencies..."
	@pip install -r backend/requirements.txt
	@echo "Installing frontend dependencies..."
	@npm install --prefix frontend

run-dev:
	@echo "Starting backend server on port 8000..."
	@PYTHONPATH=. uvicorn backend.main:app --reload &
	@echo "Starting frontend Metro bundler..."
	@npm start --prefix frontend

test:
	@echo "Running backend tests..."
	@PYTHONPATH=. pytest backend/

lint:
	@echo "Linting backend code..."
	@PYTHONPATH=. flake8 backend/ 