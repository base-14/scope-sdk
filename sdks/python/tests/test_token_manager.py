"""Tests for TokenManager class."""

import time
from unittest.mock import patch

import httpx
import pytest

from scope_client.configuration import Configuration
from scope_client.errors import InvalidCredentialsError, TokenRefreshError
from scope_client.token_manager import TokenManager


@pytest.fixture
def auth_config() -> Configuration:
    """Provide a test configuration for auth tests."""
    return Configuration(
        org_id="test_org",
        api_key="test_key",
        api_secret="test_secret",
        auth_api_url="https://auth.test.scope.io",
        token_refresh_buffer=60,
    )


class TestTokenManager:
    """Tests for TokenManager class."""

    def test_get_access_token_fetches_new_token(self, auth_config: Configuration):
        """Test that get_access_token fetches a new token when none is cached."""
        token_manager = TokenManager(auth_config)

        with patch.object(token_manager, "_fetch_token") as mock_fetch:
            mock_fetch.return_value = None
            token_manager._token_info = None

            # Manually set token after fetch
            def side_effect():
                from scope_client.token_manager import TokenInfo

                token_manager._token_info = TokenInfo(
                    access_token="test_jwt_token",
                    expires_at=time.time() + 3600,
                )

            mock_fetch.side_effect = side_effect

            token = token_manager.get_access_token()

            mock_fetch.assert_called_once()
            assert token == "test_jwt_token"

    def test_get_access_token_uses_cached_token(self, auth_config: Configuration):
        """Test that get_access_token uses cached token when valid."""
        token_manager = TokenManager(auth_config)

        from scope_client.token_manager import TokenInfo

        token_manager._token_info = TokenInfo(
            access_token="cached_token",
            expires_at=time.time() + 3600,
        )

        with patch.object(token_manager, "_fetch_token") as mock_fetch:
            token = token_manager.get_access_token()

            mock_fetch.assert_not_called()
            assert token == "cached_token"

    def test_get_access_token_refreshes_expired_token(self, auth_config: Configuration):
        """Test that get_access_token refreshes an expired token."""
        token_manager = TokenManager(auth_config)

        from scope_client.token_manager import TokenInfo

        # Set an expired token (expires_at is in the past when considering buffer)
        token_manager._token_info = TokenInfo(
            access_token="expired_token",
            expires_at=time.time() + 30,  # Less than token_refresh_buffer (60)
        )

        with patch.object(token_manager, "_fetch_token") as mock_fetch:

            def side_effect():
                token_manager._token_info = TokenInfo(
                    access_token="new_token",
                    expires_at=time.time() + 3600,
                )

            mock_fetch.side_effect = side_effect

            token = token_manager.get_access_token()

            mock_fetch.assert_called_once()
            assert token == "new_token"

    def test_needs_refresh_when_no_token(self, auth_config: Configuration):
        """Test _needs_refresh returns True when no token is cached."""
        token_manager = TokenManager(auth_config)
        assert token_manager._needs_refresh() is True

    def test_needs_refresh_when_token_valid(self, auth_config: Configuration):
        """Test _needs_refresh returns False when token is valid."""
        token_manager = TokenManager(auth_config)

        from scope_client.token_manager import TokenInfo

        token_manager._token_info = TokenInfo(
            access_token="valid_token",
            expires_at=time.time() + 3600,
        )

        assert token_manager._needs_refresh() is False

    def test_needs_refresh_when_token_expiring_soon(self, auth_config: Configuration):
        """Test _needs_refresh returns True when token is expiring soon."""
        token_manager = TokenManager(auth_config)

        from scope_client.token_manager import TokenInfo

        # Token expires in 30 seconds, buffer is 60
        token_manager._token_info = TokenInfo(
            access_token="expiring_token",
            expires_at=time.time() + 30,
        )

        assert token_manager._needs_refresh() is True


class TestTokenManagerHTTP:
    """Tests for TokenManager HTTP interactions."""

    def test_fetch_token_success(self, auth_config: Configuration, httpx_mock):
        """Test successful token fetch."""
        httpx_mock.add_response(
            method="POST",
            url="https://auth.test.scope.io/v1/auth/sdk-token",
            json={
                "access_token": "jwt_token_123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )

        token_manager = TokenManager(auth_config)
        token_manager._fetch_token()

        assert token_manager._token_info is not None
        assert token_manager._token_info.access_token == "jwt_token_123"

    def test_fetch_token_401_raises_invalid_credentials(
        self, auth_config: Configuration, httpx_mock
    ):
        """Test 401 response raises InvalidCredentialsError."""
        httpx_mock.add_response(
            method="POST",
            url="https://auth.test.scope.io/v1/auth/sdk-token",
            status_code=401,
            json={"message": "Invalid credentials"},
        )

        token_manager = TokenManager(auth_config)

        with pytest.raises(InvalidCredentialsError, match="Invalid SDK credentials"):
            token_manager._fetch_token()

    def test_fetch_token_403_raises_invalid_credentials(
        self, auth_config: Configuration, httpx_mock
    ):
        """Test 403 response raises InvalidCredentialsError."""
        httpx_mock.add_response(
            method="POST",
            url="https://auth.test.scope.io/v1/auth/sdk-token",
            status_code=403,
            json={"message": "Not authorized"},
        )

        token_manager = TokenManager(auth_config)

        with pytest.raises(InvalidCredentialsError, match="not authorized"):
            token_manager._fetch_token()

    def test_fetch_token_500_raises_token_refresh_error(
        self, auth_config: Configuration, httpx_mock
    ):
        """Test 500 response raises TokenRefreshError."""
        httpx_mock.add_response(
            method="POST",
            url="https://auth.test.scope.io/v1/auth/sdk-token",
            status_code=500,
            json={"message": "Server error"},
        )

        token_manager = TokenManager(auth_config)

        with pytest.raises(TokenRefreshError, match="Server error"):
            token_manager._fetch_token()

    def test_fetch_token_connection_error(self, auth_config: Configuration, httpx_mock):
        """Test connection error raises TokenRefreshError."""
        httpx_mock.add_exception(
            httpx.ConnectError("Connection refused"),
            url="https://auth.test.scope.io/v1/auth/sdk-token",
        )

        token_manager = TokenManager(auth_config)

        with pytest.raises(TokenRefreshError, match="Failed to connect"):
            token_manager._fetch_token()

    def test_fetch_token_timeout_error(self, auth_config: Configuration, httpx_mock):
        """Test timeout error raises TokenRefreshError."""
        httpx_mock.add_exception(
            httpx.TimeoutException("Request timed out"),
            url="https://auth.test.scope.io/v1/auth/sdk-token",
        )

        token_manager = TokenManager(auth_config)

        with pytest.raises(TokenRefreshError, match="timed out"):
            token_manager._fetch_token()

    def test_fetch_token_sends_correct_payload(self, auth_config: Configuration, httpx_mock):
        """Test that fetch_token sends the correct request payload."""
        httpx_mock.add_response(
            method="POST",
            url="https://auth.test.scope.io/v1/auth/sdk-token",
            json={"access_token": "token", "expires_in": 3600},
        )

        token_manager = TokenManager(auth_config)
        token_manager._fetch_token()

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"

        import json

        body = json.loads(request.content)
        assert body["account_id"] == "test_org"
        assert body["key_id"] == "test_key"
        assert body["key_secret"] == "test_secret"
