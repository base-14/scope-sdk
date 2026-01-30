"""Shared test fixtures for scope-client tests."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scope_client import ApiKeyCredentials, Configuration, reset_configuration
from scope_client._telemetry import Telemetry
from scope_client.cache import Cache


@pytest.fixture(autouse=True)
def reset_globals() -> Generator[None, None, None]:
    """Reset global state before each test."""
    # Clear environment variables that might affect tests
    env_vars = [
        "SCOPE_ORG_ID",
        "SCOPE_API_KEY",
        "SCOPE_API_SECRET",
        "SCOPE_API_URL",
        "SCOPE_AUTH_API_URL",
        "SCOPE_ENVIRONMENT",
        "SCOPE_TOKEN_REFRESH_BUFFER",
    ]
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
def org_id() -> str:
    """Provide a test organization ID."""
    return "test_org"


@pytest.fixture
def api_key() -> str:
    """Provide a test API key."""
    return "sk_test_123456789"


@pytest.fixture
def api_secret() -> str:
    """Provide a test API secret."""
    return "test_api_secret"


@pytest.fixture
def credentials(org_id: str, api_key: str, api_secret: str) -> ApiKeyCredentials:
    """Provide test credentials."""
    return ApiKeyCredentials(
        org_id=org_id,
        api_key=api_key,
        api_secret=api_secret,
    )


@pytest.fixture
def config(credentials: ApiKeyCredentials) -> Configuration:
    """Provide a test configuration."""
    return Configuration(
        credentials=credentials,
        base_url="https://api.test.scope.io",
        auth_api_url="https://auth.test.scope.io",
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


@pytest.fixture
def mock_token_response() -> dict[str, Any]:
    """Mock auth API token response."""
    return {
        "access_token": "test_jwt_token_abc123",
        "expires_in": 3600,
        "token_type": "Bearer",
        "client_type": "sdk",
        "environment": "production",
    }


@pytest.fixture(autouse=True)
def mock_token_manager() -> Generator[MagicMock, None, None]:
    """Mock TokenManager to avoid auth API calls in tests."""
    with patch("scope_client.connection.TokenManager") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.get_access_token.return_value = "test_jwt_token_abc123"
        mock_cls.return_value = mock_instance
        yield mock_instance
