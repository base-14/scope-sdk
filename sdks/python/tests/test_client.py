"""Tests for ScopeClient class."""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from scope_client import (
    ApiKeyCredentials,
    Configuration,
    ScopeClient,
    configure,
    reset_configuration,
)
from scope_client.errors import (
    ConfigurationError,
    MissingVariableError,
    NoProductionVersionError,
)
from scope_client.resources import PromptVersion


class TestScopeClientInit:
    """Tests for ScopeClient initialization."""

    def test_init_with_config(self, config: Configuration):
        """Test initialization with explicit configuration."""
        client = ScopeClient(config=config)
        assert client.config.credentials is not None
        assert client.config.credentials.api_key == config.credentials.api_key

    def test_init_with_credentials(self, credentials: ApiKeyCredentials):
        """Test initialization with credentials directly."""
        client = ScopeClient(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
        )
        assert client.config.credentials.api_key == credentials.api_key
        assert client.config.credentials.org_id == credentials.org_id

    def test_init_with_global_config(self, credentials: ApiKeyCredentials):
        """Test initialization with global configuration."""
        configure(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
        )
        client = ScopeClient()
        assert client.config.credentials.api_key == credentials.api_key
        assert client.config.credentials.org_id == credentials.org_id

    def test_init_with_options_override(self, config: Configuration):
        """Test initialization with options overriding config."""
        client = ScopeClient(config=config, timeout=120)
        assert client.config.timeout == 120
        assert client.config.credentials.api_key == config.credentials.api_key

    def test_init_without_credentials_raises(self):
        """Test initialization without credentials raises error."""
        reset_configuration()
        with pytest.raises(ConfigurationError):
            ScopeClient()

    def test_cache_enabled_by_default(self, config: Configuration):
        """Test cache is enabled by default."""
        client = ScopeClient(config=config)
        assert client._cache is not None

    def test_cache_disabled(self, credentials: ApiKeyCredentials):
        """Test cache can be disabled."""
        config = Configuration(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
            cache_enabled=False,
        )
        client = ScopeClient(config=config)
        assert client._cache is None

    def test_repr(self, config: Configuration):
        """Test string representation."""
        client = ScopeClient(config=config)
        repr_str = repr(client)
        assert "ScopeClient" in repr_str
        assert "api.test.scope.io" in repr_str
        assert "cache=enabled" in repr_str


class TestScopeClientGetPromptVersion:
    """Tests for ScopeClient.get_prompt_version method."""

    def test_defaults_to_production(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test that get_prompt_version defaults to production label."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("prompt-123")

        assert isinstance(version, PromptVersion)
        assert version.is_production is True

        request = httpx_mock.get_requests()[0]
        assert "/prompts/prompt-123/production" in str(request.url)

    def test_with_production_label(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test getting production version with explicit label."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("prompt-123", label="production")

        assert isinstance(version, PromptVersion)
        assert version.is_production is True

        request = httpx_mock.get_requests()[0]
        assert "/prompts/prompt-123/production" in str(request.url)

    def test_with_latest_label(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test getting latest version."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("prompt-123", label="latest")

        assert isinstance(version, PromptVersion)
        assert version.id == "version-456"
        assert version.version_number == 1

        request = httpx_mock.get_requests()[0]
        assert "/prompts/prompt-123/latest" in str(request.url)

    def test_with_specific_version(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test getting specific version."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("prompt-123", version="version-456")

        assert version.id == "version-456"

        request = httpx_mock.get_requests()[0]
        assert "/prompts/prompt-123/versions/version-456" in str(request.url)

    def test_no_production_version_error(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
    ):
        """Test no production version error."""
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "No production version"}},
        )

        client = ScopeClient(config=config)
        with pytest.raises(NoProductionVersionError) as exc_info:
            client.get_prompt_version("prompt-123")

        assert exc_info.value.prompt_id == "prompt-123"

    def test_caches_response(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test that responses are cached."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version1 = client.get_prompt_version("prompt-123")
        version2 = client.get_prompt_version("prompt-123")

        assert version1.id == version2.id
        assert len(httpx_mock.get_requests()) == 1

    def test_bypasses_cache_when_disabled(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test bypassing cache."""
        httpx_mock.add_response(json=mock_version_response)
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        client.get_prompt_version("prompt-123", cache=False)
        client.get_prompt_version("prompt-123", cache=False)

        assert len(httpx_mock.get_requests()) == 2


class TestScopeClientRenderPrompt:
    """Tests for ScopeClient.render_prompt method."""

    def test_render_prompt_production(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test rendering production version."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        rendered = client.render_prompt(
            "prompt-123",
            {"name": "Alice", "app": "Scope"},
            label="production",
        )

        assert rendered == "Hello, Alice! Welcome to Scope."

    def test_render_prompt_defaults_to_production(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test rendering defaults to production label."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        rendered = client.render_prompt(
            "prompt-123",
            {"name": "Alice", "app": "Scope"},
        )

        assert rendered == "Hello, Alice! Welcome to Scope."

        request = httpx_mock.get_requests()[0]
        assert "/prompts/prompt-123/production" in str(request.url)

    def test_render_prompt_latest(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test rendering latest version."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        rendered = client.render_prompt(
            "prompt-123",
            {"name": "Bob", "app": "Test"},
            label="latest",
        )

        assert rendered == "Hello, Bob! Welcome to Test."

    def test_render_prompt_missing_variable(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test error when variable is missing."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        with pytest.raises(MissingVariableError):
            client.render_prompt("prompt-123", {"name": "Alice"})


class TestScopeClientClearCache:
    """Tests for ScopeClient.clear_cache method."""

    def test_clear_cache(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test clearing cache."""
        httpx_mock.add_response(json=mock_version_response)
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)

        client.get_prompt_version("prompt-123")
        client.clear_cache()
        client.get_prompt_version("prompt-123")

        # Two requests because cache was cleared
        assert len(httpx_mock.get_requests()) == 2

    def test_clear_cache_disabled(self, credentials: ApiKeyCredentials):
        """Test clear_cache with disabled cache doesn't error."""
        config = Configuration(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
            cache_enabled=False,
        )
        client = ScopeClient(config=config)
        client.clear_cache()  # Should not raise


class TestScopeClientContextManager:
    """Tests for ScopeClient context manager."""

    def test_context_manager(self, config: Configuration):
        """Test using client as context manager."""
        with ScopeClient(config=config) as client:
            assert client._connection._client is None  # Lazy init

        # After exiting context, client should be cleaned up
        assert client._connection._client is None

    def test_close(self, config: Configuration):
        """Test explicit close."""
        client = ScopeClient(config=config)
        client.close()
        # Should be able to close without error


class TestScopeClientGetPromptByName:
    """Tests for fetching prompts by name instead of ID."""

    def test_get_prompt_version_latest_by_name(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test fetching latest version by prompt name."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("my-greeting-prompt", label="latest")

        assert isinstance(version, PromptVersion)
        request = httpx_mock.get_requests()[0]
        assert "/prompts/my-greeting-prompt/latest" in str(request.url)

    def test_get_prompt_version_production_by_name(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test fetching production version by prompt name."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        version = client.get_prompt_version("my-greeting-prompt")

        assert isinstance(version, PromptVersion)
        request = httpx_mock.get_requests()[0]
        assert "/prompts/my-greeting-prompt/production" in str(request.url)

    def test_cache_key_uses_identifier(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test that cache keys work correctly with names."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)

        # First call with name
        client.get_prompt_version("my-greeting-prompt")
        # Second call with same name - should use cache
        client.get_prompt_version("my-greeting-prompt")

        # Only one HTTP request should be made
        assert len(httpx_mock.get_requests()) == 1

    def test_render_prompt_by_name(
        self,
        httpx_mock: HTTPXMock,
        config: Configuration,
        mock_version_response: dict[str, Any],
    ):
        """Test rendering prompt by name."""
        httpx_mock.add_response(json=mock_version_response)

        client = ScopeClient(config=config)
        rendered = client.render_prompt(
            "my-greeting-prompt",
            {"name": "Alice", "app": "Scope"},
            label="production",
        )

        assert rendered == "Hello, Alice! Welcome to Scope."
        request = httpx_mock.get_requests()[0]
        assert "/prompts/my-greeting-prompt/production" in str(request.url)
