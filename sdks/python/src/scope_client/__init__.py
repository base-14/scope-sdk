"""Scope Client SDK for Python.

A Python SDK for the Scope Platform, providing
easy access to prompts, versions, and template rendering.

Example:
    >>> from scope_client import ScopeClient, ApiKeyCredentials
    >>>
    >>> # Create credentials from environment variables
    >>> credentials = ApiKeyCredentials.from_env()
    >>> # Or explicitly:
    >>> # credentials = ApiKeyCredentials(
    >>> #     org_id="my-org",
    >>> #     api_key="key_abc123",
    >>> #     api_secret="secret_xyz"
    >>> # )
    >>>
    >>> # Create a client
    >>> client = ScopeClient(credentials=credentials)
    >>>
    >>> # Fetch and render a prompt
    >>> version = client.get_prompt_production("greeting")
    >>> rendered = version.render({"name": "Alice"})
    >>> print(rendered)
    'Hello, Alice!'

Environment Variables:
    SCOPE_ORG_ID: Organization identifier.
    SCOPE_API_KEY: API key ID for authentication.
    SCOPE_API_SECRET: API key secret for authentication.
    SCOPE_API_URL: Base URL for the API (default: https://api.scope.io).
    SCOPE_AUTH_API_URL: Auth API URL (default: https://auth.scope.io).
    SCOPE_ENVIRONMENT: Environment name (default: production).
    SCOPE_TOKEN_REFRESH_BUFFER: Seconds before expiry to refresh token (default: 60).
"""

from typing import TYPE_CHECKING, Any, Optional

from scope_client._telemetry import (
    ErrorInfo,
    OnErrorCallback,
    OnRequestCallback,
    OnResponseCallback,
    RequestInfo,
    ResponseInfo,
    Telemetry,
)
from scope_client._version import VERSION, __version__
from scope_client.client import ScopeClient
from scope_client.configuration import Configuration, ConfigurationManager
from scope_client.credentials import ApiKeyCredentials, Credentials, CredentialsProtocol
from scope_client.errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConflictError,
    ConnectionError,
    InvalidCredentialsError,
    MissingApiKeyError,
    MissingVariableError,
    NoProductionVersionError,
    NotFoundError,
    RateLimitError,
    RenderError,
    ResourceError,
    ScopeError,
    ServerError,
    TimeoutError,
    TokenRefreshError,
    ValidationError,
)
from scope_client.resources import PromptVersion, Resource

if TYPE_CHECKING:
    pass

__all__ = [
    # Version
    "__version__",
    "VERSION",
    # Main classes
    "ScopeClient",
    "Configuration",
    # Credentials
    "ApiKeyCredentials",
    "Credentials",
    "CredentialsProtocol",
    # Resources
    "Resource",
    "PromptVersion",
    # Errors
    "ScopeError",
    "ConfigurationError",
    "MissingApiKeyError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "TokenRefreshError",
    "InvalidCredentialsError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
    "ResourceError",
    "ValidationError",
    "RenderError",
    "MissingVariableError",
    "NoProductionVersionError",
    # Telemetry
    "Telemetry",
    "RequestInfo",
    "ResponseInfo",
    "ErrorInfo",
    "OnRequestCallback",
    "OnResponseCallback",
    "OnErrorCallback",
    # Module-level functions
    "configure",
    "client",
    "configuration",
    "reset_configuration",
]


def configure(
    credentials: Optional["Credentials"] = None,
    **options: Any,
) -> Configuration:
    """Configure the global Scope client settings.

    Sets up the global configuration that will be used by clients
    created with the `client()` function.

    Args:
        credentials: Credentials instance for authentication.
        **options: Configuration options.
            base_url: Base URL for the API.
            api_version: API version string.
            timeout: Request timeout in seconds.
            open_timeout: Connection timeout in seconds.
            cache_enabled: Whether to enable caching.
            cache_ttl: Cache TTL in seconds.
            max_retries: Maximum retry attempts.
            retry_base_delay: Base delay between retries.
            retry_max_delay: Maximum delay between retries.
            telemetry_enabled: Whether to enable telemetry.
            environment: Environment name.

    Returns:
        The new Configuration instance.

    Example:
        >>> import scope_client
        >>> from scope_client import ApiKeyCredentials
        >>>
        >>> # Configure with credentials from environment
        >>> scope_client.configure(credentials=ApiKeyCredentials.from_env())
        >>>
        >>> # Or with explicit credentials
        >>> scope_client.configure(
        ...     credentials=ApiKeyCredentials(
        ...         org_id="my-org",
        ...         api_key="key_abc123",
        ...         api_secret="secret_xyz"
        ...     ),
        ...     cache_enabled=True,
        ...     cache_ttl=600
        ... )
    """
    if credentials is not None:
        options["credentials"] = credentials
    return ConfigurationManager.configure(**options)


def client(
    credentials: Optional["Credentials"] = None,
    config: Optional[Configuration] = None,
    **options: Any,
) -> ScopeClient:
    """Create a new ScopeClient instance.

    Creates a client using the provided configuration, the global
    configuration, or a combination of both.

    Args:
        credentials: Optional Credentials instance for authentication.
        config: Optional Configuration instance to use.
        **options: Configuration options to merge with the base config.

    Returns:
        A new ScopeClient instance.

    Example:
        >>> import scope_client
        >>> from scope_client import ApiKeyCredentials
        >>>
        >>> # Using credentials directly
        >>> credentials = ApiKeyCredentials.from_env()
        >>> client = scope_client.client(credentials=credentials)
        >>>
        >>> # Using global configuration
        >>> scope_client.configure(credentials=ApiKeyCredentials.from_env())
        >>> client = scope_client.client()
        >>>
        >>> # Or with per-client options
        >>> client = scope_client.client(cache_enabled=False)
    """
    return ScopeClient(credentials=credentials, config=config, **options)


def configuration() -> Configuration:
    """Get the current global configuration.

    Returns:
        The current global Configuration instance.

    Example:
        >>> import scope_client
        >>> from scope_client import ApiKeyCredentials
        >>> scope_client.configure(credentials=ApiKeyCredentials.from_env())
        >>> config = scope_client.configuration()
        >>> print(config.base_url)
        'https://api.scope.io'
    """
    return ConfigurationManager.get()


def reset_configuration() -> None:
    """Reset the global configuration to defaults.

    Clears any custom configuration and resets to default values.
    Environment variables will still be loaded when a new configuration
    is created.

    Example:
        >>> import scope_client
        >>> from scope_client import ApiKeyCredentials
        >>> scope_client.configure(credentials=ApiKeyCredentials.from_env())
        >>> scope_client.reset_configuration()
        >>> config = scope_client.configuration()
        >>> print(config.credentials)  # Will be None
    """
    ConfigurationManager.reset()
