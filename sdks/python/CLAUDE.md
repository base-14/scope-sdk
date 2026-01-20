# CLAUDE.md - Python SDK Development Guidelines

## Project Overview

This is the Python SDK for the Scope Prompt Management Platform. It provides a client library for interacting with the Scope API to manage prompts, versions, and render templates.

## Quick Commands

```bash
# Install development dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Fix lint issues automatically
make lint-fix

# Format code
make format

# Type checking
make typecheck

# Build package
make build

# Clean build artifacts
make clean
```

## Project Structure

```
sdks/python/
├── pyproject.toml              # Package config, dependencies, tool settings
├── README.md                   # Usage documentation
├── CHANGELOG.md                # Version history
├── CLAUDE.md                   # This file - development guidelines
├── Makefile                    # Build commands
├── src/
│   └── scope_client/
│       ├── __init__.py         # Module exports, version, configure()
│       ├── _version.py         # VERSION constant
│       ├── client.py           # Main ScopeClient class
│       ├── configuration.py    # Configuration dataclass
│       ├── connection.py       # HTTP client wrapper (httpx)
│       ├── cache.py            # Thread-safe TTL cache
│       ├── renderer.py         # Variable substitution
│       ├── errors.py           # Exception hierarchy
│       ├── _telemetry.py       # Request/response hooks
│       └── resources/
│           ├── __init__.py
│           ├── base.py         # Base resource class
│           ├── prompt.py       # Prompt resource
│           └── prompt_version.py  # PromptVersion resource
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── test_*.py               # Test modules
│   └── resources/
│       └── test_prompt_version.py
└── examples/
    ├── basic_usage.py
    └── error_handling.py
```

## Code Style

### Python Version
- Target Python 3.8+ for broad compatibility
- Use `from __future__ import annotations` if needed for forward references

### Formatting & Linting
- Use `ruff` for both linting and formatting
- Line length: 100 characters
- Use double quotes for strings
- Follow Google-style docstrings

### Type Hints
- All public APIs must have type hints
- Use `mypy` for type checking with strict mode
- Use `Optional` from typing for nullable types

### Docstrings
- Use Google-style docstrings
- Document all public classes, methods, and functions
- Include Args, Returns, Raises, and Example sections where appropriate

Example:
```python
def render_prompt(
    prompt_id: str,
    variables: dict[str, str],
    version: str = "production",
) -> str:
    """Render a prompt with variables.

    Fetches the specified version of a prompt and renders it
    with the provided variables.

    Args:
        prompt_id: The ID of the prompt to render.
        variables: Dictionary mapping variable names to values.
        version: Version to use - "production", "latest", or a version ID.

    Returns:
        The rendered prompt string.

    Raises:
        NotFoundError: If the prompt or version is not found.
        MissingVariableError: If required variables are missing.

    Example:
        >>> client.render_prompt("greeting", {"name": "Alice"})
        'Hello, Alice!'
    """
```

## Testing

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestScopeClient::test_get_prompt

# Run with coverage
make test-coverage
```

### Test Organization
- Use `pytest` for testing
- Use `pytest-httpx` for mocking HTTP requests
- Place fixtures in `tests/conftest.py`
- Mirror source structure in tests

### Test Naming
- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_it_tests>`

### Fixtures
Common fixtures are defined in `conftest.py`:
- `api_key`: Test API key
- `config`: Test configuration
- `cache`: Test cache instance
- `prompt_data`: Sample prompt response
- `prompt_version_data`: Sample version response

## Architecture

### Error Handling
- All SDK errors inherit from `ScopeError`
- HTTP errors map to specific exceptions (AuthenticationError, NotFoundError, etc.)
- Use `error_from_response()` to create appropriate error from HTTP status

### Configuration
- Configuration is immutable (frozen dataclass)
- Global configuration via `ConfigurationManager`
- Per-client overrides via constructor or method options
- Environment variables: `SCOPE_API_KEY`, `SCOPE_API_URL`, `SCOPE_ENVIRONMENT`

### Caching
- Thread-safe TTL-based cache
- Cache keys follow pattern: `resource_type:id:variant`
- Per-request cache control via `cache=False` or `cache_ttl=N`

### Resources
- All API responses are wrapped in Resource classes
- Base `Resource` provides dictionary-like access
- Specialized resources (`Prompt`, `PromptVersion`) add convenience methods

### Telemetry
- Optional request/response logging via callbacks
- Register callbacks with `Telemetry.on_request()`, `on_response()`, `on_error()`
- Sensitive headers are automatically redacted

## Dependencies

### Runtime
- `httpx>=0.24.0,<1.0.0` - HTTP client

### Development
- `pytest>=7.0.0` - Testing framework
- `pytest-httpx>=0.21.0` - HTTP mocking for pytest
- `pytest-cov>=4.0.0` - Coverage reporting
- `ruff>=0.1.0` - Linting and formatting
- `mypy>=1.0.0` - Type checking

## Release Process

1. Update version in `src/scope_client/_version.py`
2. Update `CHANGELOG.md`
3. Run full test suite: `make test-coverage`
4. Run lint checks: `make lint`
5. Build package: `make build`
6. Create git tag: `python-v0.x.x`
7. Push tag to trigger CI release

## Common Tasks

### Adding a New Error Type
1. Add class to `errors.py` inheriting from appropriate parent
2. Add to `error_from_response()` if HTTP-status-based
3. Export from `__init__.py`
4. Add tests to `test_errors.py`

### Adding a New Resource
1. Create class in `resources/` inheriting from `Resource`
2. Add type hints for expected attributes
3. Add convenience methods as needed
4. Export from `resources/__init__.py` and main `__init__.py`
5. Add tests to `tests/resources/`

### Adding a New Client Method
1. Add method to `ScopeClient` class
2. Follow pattern: fetch → cache → return resource
3. Document with docstring including example
4. Add tests with HTTP mocking

## Troubleshooting

### Common Issues

**Import errors after installation**
- Ensure you installed with `pip install -e .` for development

**Type errors in tests**
- Tests have relaxed type checking - check `pyproject.toml` mypy overrides

**HTTP mocking not working**
- Ensure `pytest-httpx` is installed
- Check mock URL matches actual request URL
