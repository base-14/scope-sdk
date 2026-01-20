"""Shared test fixtures for scope-client tests."""

import os
from typing import Any, Generator

import pytest

from scope_client import Configuration, reset_configuration
from scope_client._telemetry import Telemetry
from scope_client.cache import Cache


@pytest.fixture(autouse=True)
def reset_globals() -> Generator[None, None, None]:
    """Reset global state before each test."""
    # Clear environment variables that might affect tests
    env_vars = ["SCOPE_API_KEY", "SCOPE_API_URL", "SCOPE_ENVIRONMENT"]
    original_values = {var: os.environ.get(var) for var in env_vars}

    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    # Clear telemetry callbacks
    Telemetry.clear_callbacks()

    # Reset configuration
    reset_configuration()

    yield

    # Restore original environment
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def api_key() -> str:
    """Provide a test API key."""
    return "sk_test_123456789"


@pytest.fixture
def config(api_key: str) -> Configuration:
    """Provide a test configuration."""
    return Configuration(
        api_key=api_key,
        base_url="https://api.test.scope.io",
        cache_enabled=True,
        cache_ttl=300,
    )


@pytest.fixture
def cache() -> Cache:
    """Provide a test cache."""
    return Cache(ttl=60)


@pytest.fixture
def prompt_data() -> dict[str, Any]:
    """Sample prompt API response data."""
    return {
        "id": "prompt-123",
        "name": "Test Prompt",
        "description": "A test prompt for unit tests",
        "has_production_version": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def prompt_version_data() -> dict[str, Any]:
    """Sample prompt version API response data."""
    return {
        "id": "version-456",
        "prompt_id": "prompt-123",
        "version_number": 1,
        "content": "Hello, {{name}}! Welcome to {{app}}.",
        "variables": ["name", "app"],
        "status": "published",
        "is_production": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def mock_prompt_response(prompt_data: dict[str, Any]) -> dict[str, Any]:
    """Mock API response for a prompt."""
    return prompt_data


@pytest.fixture
def mock_version_response(prompt_version_data: dict[str, Any]) -> dict[str, Any]:
    """Mock API response for a prompt version."""
    return prompt_version_data


@pytest.fixture
def mock_list_response(prompt_data: dict[str, Any]) -> dict[str, Any]:
    """Mock API response for listing prompts."""
    return {
        "data": [prompt_data, {**prompt_data, "id": "prompt-456", "name": "Another Prompt"}],
        "meta": {
            "total": 2,
            "page": 1,
            "per_page": 20,
            "total_pages": 1,
        },
    }
