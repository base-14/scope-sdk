"""Credentials management for scope-client.

This module provides the credentials classes for SDK authentication.
The credential system is designed to be extensible for future auth schemes.

Example:
    >>> from scope_client import ClientCredentials
    >>>
    >>> # Create credentials explicitly
    >>> credentials = ClientCredentials(
    ...     org_id="my-org",
    ...     client_id="key_abc123",
    ...     client_secret="secret_xyz"
    ... )
    >>>
    >>> # Or load from environment variables
    >>> credentials = ClientCredentials.from_env()
"""

import os
import warnings
from typing import Any, Optional, Protocol, Union, runtime_checkable


@runtime_checkable
class CredentialsProtocol(Protocol):
    """Protocol defining the interface for all credential types.

    All credential implementations must provide these methods to be
    usable with the SDK.
    """

    @property
    def auth_type(self) -> str:
        """Return the authentication type identifier.

        Returns:
            String identifying the authentication type (e.g., 'client_credentials').
        """
        ...

    def validate(self) -> None:
        """Validate that all required credential fields are present.

        Raises:
            ConfigurationError: If required fields are missing.
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert credentials to a dictionary representation.

        Sensitive fields should be redacted in the output.

        Returns:
            Dictionary representation of the credentials.
        """
        ...


class ClientCredentials:
    """Client credentials for SDK authentication.

    This is the primary authentication method for the Scope SDK,
    using organization ID, client ID, and client secret.

    Attributes:
        org_id: Organization identifier.
        client_id: Client ID for authentication.
        client_secret: Client secret for authentication.

    Note:
        The old parameter names ``api_key`` and ``api_secret`` are still accepted
        but deprecated. Use ``client_id`` and ``client_secret`` instead.

    Example:
        >>> credentials = ClientCredentials(
        ...     org_id="my-org",
        ...     client_id="key_abc123",
        ...     client_secret="secret_xyz"
        ... )
        >>> credentials.validate()  # Raises if invalid

        >>> # Load from environment
        >>> credentials = ClientCredentials.from_env()
    """

    org_id: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]

    def __init__(
        self,
        org_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        # Handle backward-compatible parameter names
        if api_key is not None:
            if client_id is not None:
                raise TypeError("Cannot specify both 'client_id' and 'api_key'")
            warnings.warn(
                "The 'api_key' parameter is deprecated. Use 'client_id' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            client_id = api_key

        if api_secret is not None:
            if client_secret is not None:
                raise TypeError("Cannot specify both 'client_secret' and 'api_secret'")
            warnings.warn(
                "The 'api_secret' parameter is deprecated. Use 'client_secret' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            client_secret = api_secret

        object.__setattr__(self, "org_id", org_id)
        object.__setattr__(self, "client_id", client_id)
        object.__setattr__(self, "client_secret", client_secret)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(
            f"cannot set '{name}' attribute on immutable {type(self).__name__} instance"
        )

    def __delattr__(self, name: str) -> None:
        raise AttributeError(
            f"cannot delete '{name}' attribute on immutable {type(self).__name__} instance"
        )

    @property
    def api_key(self) -> Optional[str]:
        """Backward-compatible accessor for client_id (deprecated)."""
        return self.client_id

    @property
    def api_secret(self) -> Optional[str]:
        """Backward-compatible accessor for client_secret (deprecated)."""
        return self.client_secret

    @property
    def auth_type(self) -> str:
        """Return the authentication type identifier.

        Returns:
            The string 'client_credentials'.
        """
        return "client_credentials"

    def validate(self) -> None:
        """Validate that all required credential fields are present.

        Raises:
            ConfigurationError: If org_id, client_id, or client_secret is missing.
        """
        from scope_client.errors import ConfigurationError

        if not self.org_id:
            raise ConfigurationError("org_id is required")
        if not self.client_id:
            raise ConfigurationError("client_id is required")
        if not self.client_secret:
            raise ConfigurationError("client_secret is required")

    def to_dict(self) -> dict[str, Any]:
        """Convert credentials to a dictionary with redacted secret.

        Returns:
            Dictionary with org_id, client_id, and redacted client_secret.
        """
        return {
            "auth_type": self.auth_type,
            "org_id": self.org_id,
            "client_id": self.client_id,
            "client_secret": "[REDACTED]" if self.client_secret else None,
        }

    @classmethod
    def from_env(cls) -> "ClientCredentials":
        """Create credentials from environment variables.

        Reads from:
            - SCOPE_ORG_ID: Organization identifier
            - SCOPE_CLIENT_ID: Client ID (falls back to SCOPE_API_KEY with deprecation warning)
            - SCOPE_CLIENT_SECRET: Client secret (falls back to SCOPE_API_SECRET with warning)

        Returns:
            ClientCredentials instance with values from environment.

        Example:
            >>> import os
            >>> os.environ["SCOPE_ORG_ID"] = "my-org"
            >>> os.environ["SCOPE_CLIENT_ID"] = "key_abc123"
            >>> os.environ["SCOPE_CLIENT_SECRET"] = "secret_xyz"
            >>> credentials = ClientCredentials.from_env()
            >>> credentials.org_id
            'my-org'
        """
        org_id = os.environ.get("SCOPE_ORG_ID")

        client_id = os.environ.get("SCOPE_CLIENT_ID")
        if client_id is None and os.environ.get("SCOPE_API_KEY") is not None:
            warnings.warn(
                "The 'SCOPE_API_KEY' environment variable is deprecated. "
                "Use 'SCOPE_CLIENT_ID' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            client_id = os.environ.get("SCOPE_API_KEY")

        client_secret = os.environ.get("SCOPE_CLIENT_SECRET")
        if client_secret is None and os.environ.get("SCOPE_API_SECRET") is not None:
            warnings.warn(
                "The 'SCOPE_API_SECRET' environment variable is deprecated. "
                "Use 'SCOPE_CLIENT_SECRET' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            client_secret = os.environ.get("SCOPE_API_SECRET")

        return cls(
            org_id=org_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    def __repr__(self) -> str:
        """Return a string representation with redacted secret.

        Returns:
            String representation showing org_id and client_id but not secret.
        """
        return (
            f"ClientCredentials(org_id={self.org_id!r}, "
            f"client_id={self.client_id!r}, client_secret='[REDACTED]')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClientCredentials):
            return NotImplemented
        return (
            self.org_id == other.org_id
            and self.client_id == other.client_id
            and self.client_secret == other.client_secret
        )

    def __hash__(self) -> int:
        return hash((self.org_id, self.client_id, self.client_secret))


# Backward-compatible alias
ApiKeyCredentials = ClientCredentials

# Union type for all supported credential types
# This will be expanded as new auth schemes are added
Credentials = Union[ClientCredentials]
