.PHONY: help install install-dev test test-coverage lint lint-fix format typecheck build clean

# Default target
help:
	@echo "Scope Client Python SDK - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  lint-fix      Run linting and fix issues"
	@echo "  format        Format code with ruff"
	@echo "  typecheck     Run type checking with mypy"
	@echo "  build         Build package (wheel and sdist)"
	@echo "  clean         Remove build artifacts"
	@echo ""

# Install package in development mode
install:
	pip install -e .

# Install package with development dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-coverage:
	pytest tests/ -v --cov=src/scope_client --cov-report=term-missing --cov-report=html

# Run linting
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# Run linting and fix issues
lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

# Format code
format:
	ruff format src/ tests/

# Run type checking
typecheck:
	mypy src/scope_client

# Build package
build:
	pip install build
	python -m build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run all checks (lint, typecheck, test)
check: lint typecheck test
	@echo "All checks passed!"

# CI target - all checks with coverage
ci: lint typecheck test-coverage
	@echo "CI checks complete!"
