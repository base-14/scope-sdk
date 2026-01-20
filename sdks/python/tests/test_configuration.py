"""Tests for configuration module."""

import os

import pytest

from scope_client.configuration import Configuration, ConfigurationManager
from scope_client.errors import MissingApiKeyError


class TestConfiguration:
    """Tests for Configuration class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = Configuration()
        assert config.api_key is None
        assert config.base_url == "https://api.scope.io"
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

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = Configuration(
            api_key="sk_test_123",
            base_url="https://custom.api.io",
            timeout=60,
            cache_enabled=False,
        )
        assert config.api_key == "sk_test_123"
        assert config.base_url == "https://custom.api.io"
        assert config.timeout == 60
        assert config.cache_enabled is False

    def test_environment_variable_api_key(self):
        """Test API key from environment variable."""
        os.environ["SCOPE_API_KEY"] = "sk_env_key"
        config = Configuration()
        assert config.api_key == "sk_env_key"

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

    def test_explicit_values_override_env(self):
        """Test that explicit values override environment variables."""
        os.environ["SCOPE_API_KEY"] = "sk_env_key"
        config = Configuration(api_key="sk_explicit_key")
        assert config.api_key == "sk_explicit_key"

    def test_immutability(self):
        """Test that configuration is immutable."""
        config = Configuration(api_key="sk_test")
        with pytest.raises(AttributeError):
            config.api_key = "new_key"

    def test_merge_creates_new_instance(self):
        """Test that merge creates a new configuration."""
        config1 = Configuration(api_key="sk_test", timeout=30)
        config2 = config1.merge(timeout=60)

        assert config1.timeout == 30
        assert config2.timeout == 60
        assert config1 is not config2
        assert config2.api_key == "sk_test"  # Preserved from original

    def test_merge_multiple_values(self):
        """Test merging multiple values."""
        config1 = Configuration(api_key="sk_test")
        config2 = config1.merge(
            timeout=60,
            cache_enabled=False,
            max_retries=5,
        )
        assert config2.timeout == 60
        assert config2.cache_enabled is False
        assert config2.max_retries == 5

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Configuration(api_key="sk_test", timeout=60)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["api_key"] == "sk_test"
        assert data["timeout"] == 60
        assert "base_url" in data
        assert "cache_enabled" in data

    def test_api_url_property(self):
        """Test api_url property."""
        config = Configuration(base_url="https://api.scope.io", api_version="v2")
        assert config.api_url == "https://api.scope.io/v2"

    def test_validate_with_api_key(self):
        """Test validation passes with API key."""
        config = Configuration(api_key="sk_test")
        config.validate()  # Should not raise

    def test_validate_without_api_key(self):
        """Test validation fails without API key."""
        config = Configuration()
        with pytest.raises(MissingApiKeyError):
            config.validate()


class TestConfigurationManager:
    """Tests for ConfigurationManager class."""

    def test_get_returns_default_config(self):
        """Test get returns default configuration."""
        config = ConfigurationManager.get()
        assert isinstance(config, Configuration)
        assert config.base_url == "https://api.scope.io"

    def test_set_and_get(self):
        """Test setting and getting configuration."""
        custom_config = Configuration(api_key="sk_test_123")
        ConfigurationManager.set(custom_config)

        retrieved = ConfigurationManager.get()
        assert retrieved.api_key == "sk_test_123"

    def test_reset(self):
        """Test resetting configuration."""
        ConfigurationManager.set(Configuration(api_key="sk_test"))
        ConfigurationManager.reset()

        config = ConfigurationManager.get()
        assert config.api_key is None  # Back to default

    def test_configure_from_scratch(self):
        """Test configure when no existing config."""
        ConfigurationManager.reset()
        config = ConfigurationManager.configure(api_key="sk_new", timeout=90)

        assert config.api_key == "sk_new"
        assert config.timeout == 90

    def test_configure_merges_existing(self):
        """Test configure merges with existing config."""
        ConfigurationManager.configure(api_key="sk_original", timeout=30)
        config = ConfigurationManager.configure(timeout=60)

        assert config.api_key == "sk_original"  # Preserved
        assert config.timeout == 60  # Updated

    def test_configure_updates_global(self):
        """Test that configure updates the global configuration."""
        ConfigurationManager.configure(api_key="sk_global")
        config = ConfigurationManager.get()
        assert config.api_key == "sk_global"
