"""Tests for credentials module."""

import os

import pytest

from scope_client import ApiKeyCredentials, CredentialsProtocol
from scope_client.errors import ConfigurationError


class TestApiKeyCredentials:
    """Tests for ApiKeyCredentials class."""

    def test_create_with_values(self):
        """Test creating credentials with explicit values."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        assert credentials.org_id == "my-org"
        assert credentials.api_key == "key_abc123"
        assert credentials.api_secret == "secret_xyz"

    def test_default_values_are_none(self):
        """Test that default values are None."""
        credentials = ApiKeyCredentials()
        assert credentials.org_id is None
        assert credentials.api_key is None
        assert credentials.api_secret is None

    def test_auth_type_property(self):
        """Test auth_type property."""
        credentials = ApiKeyCredentials()
        assert credentials.auth_type == "api_key"

    def test_validate_success(self):
        """Test validation passes with all required fields."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        credentials.validate()  # Should not raise

    def test_validate_missing_org_id(self):
        """Test validation fails without org_id."""
        credentials = ApiKeyCredentials(
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        with pytest.raises(ConfigurationError, match="org_id is required"):
            credentials.validate()

    def test_validate_missing_api_key(self):
        """Test validation fails without api_key."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_secret="secret_xyz",
        )
        with pytest.raises(ConfigurationError, match="api_key is required"):
            credentials.validate()

    def test_validate_missing_api_secret(self):
        """Test validation fails without api_secret."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
        )
        with pytest.raises(ConfigurationError, match="api_secret is required"):
            credentials.validate()

    def test_to_dict_redacts_secret(self):
        """Test to_dict redacts the api_secret."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        result = credentials.to_dict()

        assert result["auth_type"] == "api_key"
        assert result["org_id"] == "my-org"
        assert result["api_key"] == "key_abc123"
        assert result["api_secret"] == "[REDACTED]"

    def test_to_dict_with_none_secret(self):
        """Test to_dict handles None secret."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
        )
        result = credentials.to_dict()
        assert result["api_secret"] is None

    def test_from_env(self):
        """Test loading credentials from environment variables."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        os.environ["SCOPE_API_KEY"] = "env-key"
        os.environ["SCOPE_API_SECRET"] = "env-secret"

        credentials = ApiKeyCredentials.from_env()

        assert credentials.org_id == "env-org"
        assert credentials.api_key == "env-key"
        assert credentials.api_secret == "env-secret"

    def test_from_env_partial(self):
        """Test from_env with partial environment variables."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        # API_KEY and API_SECRET not set

        credentials = ApiKeyCredentials.from_env()

        assert credentials.org_id == "env-org"
        assert credentials.api_key is None
        assert credentials.api_secret is None

    def test_immutability(self):
        """Test that credentials are immutable (frozen dataclass)."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        with pytest.raises(AttributeError):
            credentials.api_key = "new_key"

    def test_repr_redacts_secret(self):
        """Test that repr redacts the api_secret."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        repr_str = repr(credentials)

        assert "my-org" in repr_str
        assert "key_abc123" in repr_str
        assert "secret_xyz" not in repr_str
        assert "[REDACTED]" in repr_str

    def test_implements_protocol(self):
        """Test that ApiKeyCredentials implements CredentialsProtocol."""
        credentials = ApiKeyCredentials(
            org_id="my-org",
            api_key="key_abc123",
            api_secret="secret_xyz",
        )
        assert isinstance(credentials, CredentialsProtocol)


class TestCredentialsProtocol:
    """Tests for CredentialsProtocol."""

    def test_protocol_methods_exist(self):
        """Test that the protocol requires expected methods."""
        credentials = ApiKeyCredentials()

        # Check methods exist and are callable
        assert hasattr(credentials, "auth_type")
        assert hasattr(credentials, "validate")
        assert hasattr(credentials, "to_dict")
        assert callable(credentials.validate)
        assert callable(credentials.to_dict)
