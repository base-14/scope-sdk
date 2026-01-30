"""Credentials management for scope-client.

This module provides the credentials classes for SDK authentication.
The credential system is designed to be extensible for future auth schemes.

Example:
    >>> from scope_client import ApiKeyCredentials
    >>>
    >>> # Create credentials explicitly
    >>> credentials = ApiKeyCredentials(
    ...     org_id="my-org",
    ...     api_key="key_abc123",
    ...     api_secret="secret_xyz"
    ... )
    >>>
    >>> # Or load from environment variables
    >>> credentials = ApiKeyCredentials.from_env()
"""

import os
from dataclasses import dataclass
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
            String identifying the authentication type (e.g., 'api_key').
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


@dataclass(frozen=True)
class ApiKeyCredentials:
    """API key-based credentials for SDK authentication.

    This is the primary authentication method for the Scope SDK,
    using organization ID, API key, and API secret.

    Attributes:
        org_id: Organization identifier.
        api_key: API key ID for authentication.
        api_secret: API key secret for authentication.

    Example:
        >>> credentials = ApiKeyCredentials(
        ...     org_id="my-org",
        ...     api_key="key_abc123",
        ...     api_secret="secret_xyz"
        ... )
        >>> credentials.validate()  # Raises if invalid

        >>> # Load from environment
        >>> credentials = ApiKeyCredentials.from_env()
    """

    org_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

    @property
    def auth_type(self) -> str:
        """Return the authentication type identifier.

        Returns:
            The string 'api_key'.
        """
        return "api_key"

    def validate(self) -> None:
        """Validate that all required credential fields are present.

        Raises:
            ConfigurationError: If org_id, api_key, or api_secret is missing.
        """
        from scope_client.errors import ConfigurationError

        if not self.org_id:
            raise ConfigurationError("org_id is required")
        if not self.api_key:
            raise ConfigurationError("api_key is required")
        if not self.api_secret:
            raise ConfigurationError("api_secret is required")

    def to_dict(self) -> dict[str, Any]:
        """Convert credentials to a dictionary with redacted secret.

        Returns:
            Dictionary with org_id, api_key, and redacted api_secret.
        """
        return {
            "auth_type": self.auth_type,
            "org_id": self.org_id,
            "api_key": self.api_key,
            "api_secret": "[REDACTED]" if self.api_secret else None,
        }

    @classmethod
    def from_env(cls) -> "ApiKeyCredentials":
        """Create credentials from environment variables.

        Reads from:
            - SCOPE_ORG_ID: Organization identifier
            - SCOPE_API_KEY: API key ID
            - SCOPE_API_SECRET: API key secret

        Returns:
            ApiKeyCredentials instance with values from environment.

        Example:
            >>> import os
            >>> os.environ["SCOPE_ORG_ID"] = "my-org"
            >>> os.environ["SCOPE_API_KEY"] = "key_abc123"
            >>> os.environ["SCOPE_API_SECRET"] = "secret_xyz"
            >>> credentials = ApiKeyCredentials.from_env()
            >>> credentials.org_id
            'my-org'
        """
        return cls(
            org_id=os.environ.get("SCOPE_ORG_ID"),
            api_key=os.environ.get("SCOPE_API_KEY"),
            api_secret=os.environ.get("SCOPE_API_SECRET"),
        )

    def __repr__(self) -> str:
        """Return a string representation with redacted secret.

        Returns:
            String representation showing org_id and api_key but not secret.
        """
        return (
            f"ApiKeyCredentials(org_id={self.org_id!r}, "
            f"api_key={self.api_key!r}, api_secret='[REDACTED]')"
        )


# Union type for all supported credential types
# This will be expanded as new auth schemes are added
Credentials = Union[ApiKeyCredentials]
