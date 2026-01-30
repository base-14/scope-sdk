"""Token management for SDK authentication.

This module provides the TokenManager class for handling JWT token
lifecycle including fetching, caching, and refreshing tokens.
"""

import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import httpx

from scope_client.errors import InvalidCredentialsError, TokenRefreshError

if TYPE_CHECKING:
    from scope_client.configuration import Configuration


@dataclass
class TokenInfo:
    """Cached token information."""

    access_token: str
    expires_at: float  # Unix timestamp


class TokenManager:
    """Manages SDK authentication tokens.

    Handles token fetching, caching, and automatic refresh before expiry.
    Thread-safe for concurrent access.

    Args:
        config: Configuration instance with credentials.

    Example:
        >>> from scope_client import ApiKeyCredentials
        >>> from scope_client.configuration import Configuration
        >>> credentials = ApiKeyCredentials(
        ...     org_id="my-org",
        ...     api_key="key_abc123",
        ...     api_secret="secret_xyz"
        ... )
        >>> config = Configuration(credentials=credentials)
        >>> token_manager = TokenManager(config)
        >>> token = token_manager.get_access_token()
    """

    def __init__(self, config: "Configuration") -> None:
        self._config = config
        self._lock = threading.Lock()
        self._token_info: Optional[TokenInfo] = None

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid JWT access token.

        Raises:
            TokenRefreshError: If token refresh fails.
            InvalidCredentialsError: If credentials are invalid.
        """
        with self._lock:
            if self._needs_refresh():
                self._fetch_token()
            assert self._token_info is not None
            return self._token_info.access_token

    def _needs_refresh(self) -> bool:
        """Check if the token needs to be refreshed.

        Returns:
            True if token is missing or about to expire.
        """
        if self._token_info is None:
            return True
        return time.time() >= (self._token_info.expires_at - self._config.token_refresh_buffer)

    def _fetch_token(self) -> None:
        """Fetch a new token from the auth API.

        Raises:
            TokenRefreshError: If token fetch fails.
            InvalidCredentialsError: If credentials are invalid.
        """
        url = f"{self._config.auth_api_url}/v1/auth/sdk-token"
        credentials = self._config.credentials

        try:
            with httpx.Client(
                timeout=httpx.Timeout(
                    timeout=self._config.timeout,
                    connect=self._config.open_timeout,
                )
            ) as client:
                response = client.post(
                    url,
                    json={
                        "account_id": credentials.org_id,
                        "key_id": credentials.api_key,
                        "key_secret": credentials.api_secret,
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

                self._handle_token_response(response)

        except httpx.ConnectError as e:
            raise TokenRefreshError(message=f"Failed to connect to auth API: {e}") from e
        except httpx.TimeoutException as e:
            raise TokenRefreshError(message=f"Auth API request timed out: {e}") from e

    def _handle_token_response(self, response: httpx.Response) -> None:
        """Handle the token response from the auth API.

        Args:
            response: HTTP response from auth API.

        Raises:
            TokenRefreshError: If response indicates failure.
            InvalidCredentialsError: If credentials are invalid.
        """
        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            expires_in = data.get("expires_in", 300)
            self._token_info = TokenInfo(
                access_token=access_token,
                expires_at=time.time() + expires_in,
            )
        elif response.status_code == 401:
            raise InvalidCredentialsError(message="Invalid SDK credentials")
        elif response.status_code == 403:
            raise InvalidCredentialsError(message="SDK credentials are not authorized")
        else:
            try:
                data = response.json()
                message = data.get("message") or data.get("error")
            except Exception:
                message = None

            if not message:
                message = f"Token refresh failed (HTTP {response.status_code})"

            raise TokenRefreshError(message=message)
