"""Tests for credentials module."""

import os
import warnings

import pytest

from scope_client import ApiKeyCredentials, ClientCredentials, CredentialsProtocol
from scope_client.errors import ConfigurationError


class TestClientCredentials:
    """Tests for ClientCredentials class."""

    def test_create_with_values(self):
        """Test creating credentials with explicit values."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        assert credentials.org_id == "my-org"
        assert credentials.client_id == "key_abc123"
        assert credentials.client_secret == "secret_xyz"

    def test_default_values_are_none(self):
        """Test that default values are None."""
        credentials = ClientCredentials()
        assert credentials.org_id is None
        assert credentials.client_id is None
        assert credentials.client_secret is None

    def test_auth_type_property(self):
        """Test auth_type property."""
        credentials = ClientCredentials()
        assert credentials.auth_type == "client_credentials"

    def test_validate_success(self):
        """Test validation passes with all required fields."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        credentials.validate()  # Should not raise

    def test_validate_missing_org_id(self):
        """Test validation fails without org_id."""
        credentials = ClientCredentials(
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        with pytest.raises(ConfigurationError, match="org_id is required"):
            credentials.validate()

    def test_validate_missing_client_id(self):
        """Test validation fails without client_id."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_secret="secret_xyz",
        )
        with pytest.raises(ConfigurationError, match="client_id is required"):
            credentials.validate()

    def test_validate_missing_client_secret(self):
        """Test validation fails without client_secret."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
        )
        with pytest.raises(ConfigurationError, match="client_secret is required"):
            credentials.validate()

    def test_to_dict_redacts_secret(self):
        """Test to_dict redacts the client_secret."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        result = credentials.to_dict()

        assert result["auth_type"] == "client_credentials"
        assert result["org_id"] == "my-org"
        assert result["client_id"] == "key_abc123"
        assert result["client_secret"] == "[REDACTED]"

    def test_to_dict_with_none_secret(self):
        """Test to_dict handles None secret."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
        )
        result = credentials.to_dict()
        assert result["client_secret"] is None

    def test_from_env(self):
        """Test loading credentials from environment variables."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        os.environ["SCOPE_CLIENT_ID"] = "env-key"
        os.environ["SCOPE_CLIENT_SECRET"] = "env-secret"

        credentials = ClientCredentials.from_env()

        assert credentials.org_id == "env-org"
        assert credentials.client_id == "env-key"
        assert credentials.client_secret == "env-secret"

    def test_from_env_partial(self):
        """Test from_env with partial environment variables."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        # CLIENT_ID and CLIENT_SECRET not set

        credentials = ClientCredentials.from_env()

        assert credentials.org_id == "env-org"
        assert credentials.client_id is None
        assert credentials.client_secret is None

    def test_immutability(self):
        """Test that credentials are immutable."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        with pytest.raises(AttributeError):
            credentials.client_id = "new_key"

    def test_repr_redacts_secret(self):
        """Test that repr redacts the client_secret."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        repr_str = repr(credentials)

        assert "my-org" in repr_str
        assert "key_abc123" in repr_str
        assert "secret_xyz" not in repr_str
        assert "[REDACTED]" in repr_str
        assert "ClientCredentials" in repr_str

    def test_implements_protocol(self):
        """Test that ClientCredentials implements CredentialsProtocol."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        assert isinstance(credentials, CredentialsProtocol)


class TestBackwardCompatibility:
    """Tests for backward-compatible parameter and attribute names."""

    def test_old_param_names_work_with_deprecation_warning(self):
        """Test old parameter names (api_key, api_secret) still work."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            credentials = ClientCredentials(
                org_id="my-org",
                api_key="key_abc123",
                api_secret="secret_xyz",
            )

        assert credentials.client_id == "key_abc123"
        assert credentials.client_secret == "secret_xyz"
        assert len(w) == 2
        assert issubclass(w[0].category, DeprecationWarning)
        assert "api_key" in str(w[0].message)
        assert issubclass(w[1].category, DeprecationWarning)
        assert "api_secret" in str(w[1].message)

    def test_old_property_accessors_still_work(self):
        """Test .api_key and .api_secret properties delegate correctly."""
        credentials = ClientCredentials(
            org_id="my-org",
            client_id="key_abc123",
            client_secret="secret_xyz",
        )
        assert credentials.api_key == "key_abc123"
        assert credentials.api_secret == "secret_xyz"

    def test_cannot_specify_both_client_id_and_api_key(self):
        """Test error when both client_id and api_key are specified."""
        with pytest.raises(TypeError, match="Cannot specify both"):
            ClientCredentials(
                org_id="my-org",
                client_id="key1",
                api_key="key2",
            )

    def test_cannot_specify_both_client_secret_and_api_secret(self):
        """Test error when both client_secret and api_secret are specified."""
        with pytest.raises(TypeError, match="Cannot specify both"):
            ClientCredentials(
                org_id="my-org",
                client_secret="secret1",
                api_secret="secret2",
            )

    def test_from_env_falls_back_to_old_env_vars(self):
        """Test from_env falls back to SCOPE_API_KEY/SCOPE_API_SECRET."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        os.environ["SCOPE_API_KEY"] = "env-key"
        os.environ["SCOPE_API_SECRET"] = "env-secret"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            credentials = ClientCredentials.from_env()

        assert credentials.org_id == "env-org"
        assert credentials.client_id == "env-key"
        assert credentials.client_secret == "env-secret"
        assert len(w) == 2
        assert issubclass(w[0].category, DeprecationWarning)
        assert "SCOPE_API_KEY" in str(w[0].message)
        assert issubclass(w[1].category, DeprecationWarning)
        assert "SCOPE_API_SECRET" in str(w[1].message)

    def test_from_env_prefers_new_env_vars(self):
        """Test from_env prefers SCOPE_CLIENT_ID over SCOPE_API_KEY."""
        os.environ["SCOPE_ORG_ID"] = "env-org"
        os.environ["SCOPE_CLIENT_ID"] = "new-key"
        os.environ["SCOPE_API_KEY"] = "old-key"
        os.environ["SCOPE_CLIENT_SECRET"] = "new-secret"
        os.environ["SCOPE_API_SECRET"] = "old-secret"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            credentials = ClientCredentials.from_env()

        assert credentials.client_id == "new-key"
        assert credentials.client_secret == "new-secret"
        # No deprecation warnings when new env vars are present
        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(dep_warnings) == 0

    def test_api_key_credentials_is_alias(self):
        """Test that ApiKeyCredentials is an alias for ClientCredentials."""
        assert ApiKeyCredentials is ClientCredentials


class TestCredentialsProtocol:
    """Tests for CredentialsProtocol."""

    def test_protocol_methods_exist(self):
        """Test that the protocol requires expected methods."""
        credentials = ClientCredentials()

        # Check methods exist and are callable
        assert hasattr(credentials, "auth_type")
        assert hasattr(credentials, "validate")
        assert hasattr(credentials, "to_dict")
        assert callable(credentials.validate)
        assert callable(credentials.to_dict)
