# Bench Management App Makefile
# Simplifies common development and deployment tasks

# Variables
PYTHON = python
PIP = $(PYTHON) -m pip
PYTEST = pytest
PYTEST_ARGS = -v
DOCKER_COMPOSE = docker-compose
PYTEST_COV_ARGS = --cov=app --cov-report=term-missing
APP_DIR = .
DOCKER_COMPOSE_FILE = docker-compose.yml

.PHONY: help setup clean test test-cov lint format start stop logs shell db-shell db-migrate install update-deps build

# Default target when just running 'make'
help:
	@echo "Available targets:"
	@echo "  setup        - Install dependencies and prepare development environment"
	@echo "  clean        - Remove Python compiled files and caches"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Check code with flake8"
	@echo "  format       - Format code with black"
	@echo "  start        - Start the application with Docker Compose"
	@echo "  stop         - Stop the application"
	@echo "  logs         - Show application logs"
	@echo "  shell        - Enter Python shell with application context"
	@echo "  db-shell     - Access PostgreSQL database shell"
	@echo "  db-migrate   - Apply migrations to database"
	@echo "  install      - Install Python dependencies"
	@echo "  update-deps  - Update dependencies"
	@echo "  build        - Build Docker containers"
	@echo "  dev          - Start FastAPI development server (not in Docker)"

# Setup development environment
setup: install

# Clean Python cache files
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleaned!"

# Run tests
test:
	@echo "Running tests..."
	$(PYTEST) $(PYTEST_ARGS)

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	$(PYTEST) $(PYTEST_ARGS) $(PYTEST_COV_ARGS)

# Lint code
lint:
	@echo "Linting code with flake8..."
	flake8 $(APP_DIR)

# Format code
format:
	@echo "Formatting code with black..."
	black $(APP_DIR)

# Start the application with Docker Compose
start:
	@echo "Starting application with Docker Compose..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "Application is running. API available at http://localhost:8000"
	@echo "API documentation available at http://localhost:8000/docs"
	@echo "Use 'make logs' to see application logs"

# Stop the application
stop:
	@echo "Stopping application..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

# Show application logs
logs:
	@echo "Showing application logs..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

# Enter Python shell with application context
shell:
	@echo "Starting Python shell with application context..."
	$(PYTHON) -c "import sys; sys.path.insert(0, '$(APP_DIR)'); \
		print('Application context available. Import app modules with: from app import ...');" -i

# Access PostgreSQL database shell
db-shell:
	@echo "Connecting to PostgreSQL shell..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec db psql -U postgres -d bench_management

# Apply migrations to database
db-migrate:
	@echo "Applying migrations to database..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec db psql -U postgres -d bench_management -f /docker-entrypoint-initdb.d/create_tables.sql

# Install Python dependencies
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "Installing development dependencies..."
	$(PIP) install pytest pytest-cov flake8 black
	@echo "Dependencies installed!"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	$(PIP) install --upgrade -r requirements.txt

# Build Docker containers
build:
	@echo "Building Docker containers..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up

# Start FastAPI development server (not in Docker)
dev:
	@echo "Starting FastAPI development server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000