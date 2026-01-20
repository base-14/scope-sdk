.PHONY: help install install-dev test test-coverage lint lint-fix format typecheck build clean venv

# Virtual environment directory
VENV_DIR := .venv

# Detect system Python first
SYS_PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

# Detect if we're in a virtual environment
IN_VENV := $(shell $(SYS_PYTHON) -c "import sys; print('1' if sys.prefix != sys.base_prefix else '')" 2>/dev/null)

# Detect Python command (prefer venv python if it exists and we're not already in a venv)
ifeq ($(IN_VENV),)
  ifneq ($(wildcard $(VENV_DIR)/bin/python),)
    PYTHON := $(VENV_DIR)/bin/python
  else
    PYTHON := $(SYS_PYTHON)
  endif
else
  PYTHON := $(SYS_PYTHON)
endif

# Use python -m pip for reliability across environments
PIP := $(PYTHON) -m pip

# For tools installed via pip, use python -m for reliability
RUFF := $(PYTHON) -m ruff
PYTEST := $(PYTHON) -m pytest
MYPY := $(PYTHON) -m mypy

# Default target
help:
	@echo "Scope Client Python SDK - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  venv          Create virtual environment (recommended for local dev)"
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
	@echo "Local Development (Homebrew Python):"
	@echo "  make venv && source .venv/bin/activate && make install-dev"
	@echo ""

# Install package in development mode
install:
	$(PIP) install -e .

# Install package with development dependencies
install-dev:
	$(PIP) install -e ".[dev]"

# Create virtual environment
venv:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
	else \
		echo "Creating virtual environment at $(VENV_DIR)..."; \
		$(shell command -v python3 2>/dev/null || command -v python 2>/dev/null) -m venv $(VENV_DIR); \
		echo "Virtual environment created. Activate with: source $(VENV_DIR)/bin/activate"; \
	fi

# Run tests
test:
	$(PYTEST) tests/ -v

# Run tests with coverage
test-coverage:
	$(PYTEST) tests/ -v --cov=src/scope_client --cov-report=term-missing --cov-report=html

# Run linting
lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

# Run linting and fix issues
lint-fix:
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

# Format code
format:
	$(RUFF) format src/ tests/

# Run type checking
typecheck:
	$(MYPY) src/scope_client

# Build package
build:
	$(PIP) install build
	$(PYTHON) -m build

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
