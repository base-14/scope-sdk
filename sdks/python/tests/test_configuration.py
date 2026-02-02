"""Tests for configuration module."""

import os

import pytest

from scope_client import ApiKeyCredentials
from scope_client.configuration import Configuration, ConfigurationManager
from scope_client.errors import ConfigurationError


class TestConfiguration:
    """Tests for Configuration class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = Configuration()
        assert config.credentials is None
        assert config.base_url is None  # Required, no default
        assert config.auth_api_url is None  # Required, no default
        assert config.api_version == "v1"
        assert config.timeout == 30
        assert config.open_timeout == 10
        assert config.cache_enabled is True
        assert config.cache_ttl == 300
        assert config.max_retries == 3
        assert config.retry_base_delay == 0.5
        assert config.retry_max_delay == 30.0
        assert config.telemetry_enabled is True
        assert config.environment == "production"

    def test_custom_values(self, credentials: ApiKeyCredentials):
        """Test configuration with custom values."""
        config = Configuration(
            credentials=credentials,
            base_url="https://custom.api.io",
            timeout=60,
            cache_enabled=False,
        )
        assert config.credentials.api_key == credentials.api_key
        assert config.base_url == "https://custom.api.io"
        assert config.timeout == 60
        assert config.cache_enabled is False

    def test_environment_variable_api_url(self):
        """Test API URL from environment variable."""
        os.environ["SCOPE_API_URL"] = "https://env.api.io/"
        config = Configuration()
        assert config.base_url == "https://env.api.io"  # Trailing slash removed

    def test_environment_variable_environment(self):
        """Test environment from environment variable."""
        os.environ["SCOPE_ENVIRONMENT"] = "staging"
        config = Configuration()
        assert config.environment == "staging"

    def test_explicit_values_override_env(self, credentials: ApiKeyCredentials):
        """Test that explicit values override environment variables."""
        os.environ["SCOPE_API_URL"] = "https://env.api.io"
        config = Configuration(credentials=credentials, base_url="https://explicit.api.io")
        assert config.base_url == "https://explicit.api.io"

    def test_immutability(self, credentials: ApiKeyCredentials):
        """Test that configuration is immutable."""
        config = Configuration(credentials=credentials)
        with pytest.raises(AttributeError):
            config.base_url = "new_url"

    def test_merge_creates_new_instance(self, credentials: ApiKeyCredentials):
        """Test that merge creates a new configuration."""
        config1 = Configuration(credentials=credentials, timeout=30)
        config2 = config1.merge(timeout=60)

        assert config1.timeout == 30
        assert config2.timeout == 60
        assert config1 is not config2
        assert config2.credentials.api_key == credentials.api_key  # Preserved from original

    def test_merge_multiple_values(self, credentials: ApiKeyCredentials):
        """Test merging multiple values."""
        config1 = Configuration(credentials=credentials)
        config2 = config1.merge(
            timeout=60,
            cache_enabled=False,
            max_retries=5,
        )
        assert config2.timeout == 60
        assert config2.cache_enabled is False
        assert config2.max_retries == 5

    def test_to_dict(self, credentials: ApiKeyCredentials):
        """Test converting configuration to dictionary."""
        config = Configuration(credentials=credentials, timeout=60)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["credentials"]["api_key"] == credentials.api_key
        assert data["credentials"]["api_secret"] == "[REDACTED]"
        assert data["timeout"] == 60
        assert "base_url" in data
        assert "cache_enabled" in data

    def test_api_url_property(self, credentials: ApiKeyCredentials):
        """Test api_url property."""
        config = Configuration(
            credentials=credentials,
            base_url="https://api.scope.io",
            api_version="v2",
        )
        assert config.api_url == "https://api.scope.io/api/v2"

    def test_validate_with_credentials(self, credentials: ApiKeyCredentials):
        """Test validation passes with all required fields."""
        config = Configuration(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
        )
        config.validate()  # Should not raise

    def test_validate_without_credentials(self):
        """Test validation fails without credentials."""
        config = Configuration()
        with pytest.raises(ConfigurationError, match="credentials is required"):
            config.validate()

    def test_validate_with_incomplete_credentials(self):
        """Test validation fails with incomplete credentials."""
        credentials = ApiKeyCredentials(org_id="test_org")  # Missing api_key and api_secret
        config = Configuration(
            credentials=credentials,
            base_url="https://api.scope.io",
            auth_api_url="https://auth.scope.io",
        )
        with pytest.raises(ConfigurationError, match="api_key is required"):
            config.validate()

    def test_validate_without_base_url(self, credentials: ApiKeyCredentials):
        """Test validation fails without base_url."""
        config = Configuration(credentials=credentials, auth_api_url="https://auth.scope.io")
        with pytest.raises(ConfigurationError, match="base_url is required"):
            config.validate()

    def test_validate_without_auth_api_url(self, credentials: ApiKeyCredentials):
        """Test validation fails without auth_api_url."""
        config = Configuration(credentials=credentials, base_url="https://api.scope.io")
        with pytest.raises(ConfigurationError, match="auth_api_url is required"):
            config.validate()


class TestConfigurationManager:
    """Tests for ConfigurationManager class."""

    def test_get_returns_default_config(self):
        """Test get returns default configuration."""
        config = ConfigurationManager.get()
        assert isinstance(config, Configuration)
        assert config.base_url is None  # Required, no default
        assert config.auth_api_url is None  # Required, no default

    def test_set_and_get(self, credentials: ApiKeyCredentials):
        """Test setting and getting configuration."""
        custom_config = Configuration(credentials=credentials)
        ConfigurationManager.set(custom_config)

        retrieved = ConfigurationManager.get()
        assert retrieved.credentials.api_key == credentials.api_key

    def test_reset(self, credentials: ApiKeyCredentials):
        """Test resetting configuration."""
        ConfigurationManager.set(Configuration(credentials=credentials))
        ConfigurationManager.reset()

        config = ConfigurationManager.get()
        assert config.credentials is None  # Back to default

    def test_configure_from_scratch(self, credentials: ApiKeyCredentials):
        """Test configure when no existing config."""
        ConfigurationManager.reset()
        config = ConfigurationManager.configure(credentials=credentials, timeout=90)

        assert config.credentials.api_key == credentials.api_key
        assert config.timeout == 90

    def test_configure_merges_existing(self, credentials: ApiKeyCredentials):
        """Test configure merges with existing config."""
        ConfigurationManager.configure(credentials=credentials, timeout=30)
        config = ConfigurationManager.configure(timeout=60)

        assert config.credentials.api_key == credentials.api_key  # Preserved
        assert config.timeout == 60  # Updated

    def test_configure_updates_global(self, credentials: ApiKeyCredentials):
        """Test that configure updates the global configuration."""
        ConfigurationManager.configure(credentials=credentials)
        config = ConfigurationManager.get()
        assert config.credentials.api_key == credentials.api_key
