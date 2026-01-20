"""Scope Client SDK for Python.

A Python SDK for the Scope Platform, providing
easy access to prompts, versions, and template rendering.

Example:
    >>> import scope_client
    >>> scope_client.configure(api_key="sk_test_123")
    >>> client = scope_client.client()

    >>> # Fetch and render a prompt
    >>> version = client.get_prompt_production("greeting")
    >>> rendered = version.render({"name": "Alice"})
    >>> print(rendered)
    'Hello, Alice!'

Environment Variables:
    SCOPE_API_KEY: API key for authentication.
    SCOPE_API_URL: Base URL for the API (default: https://api.scope.io).
    SCOPE_ENVIRONMENT: Environment name (default: production).
"""

from typing import Any, Optional

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
from scope_client.errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConflictError,
    ConnectionError,
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
    ValidationError,
)
from scope_client.resources import Prompt, PromptVersion, Resource

__all__ = [
    # Version
    "__version__",
    "VERSION",
    # Main classes
    "ScopeClient",
    "Configuration",
    # Resources
    "Resource",
    "Prompt",
    "PromptVersion",
    # Errors
    "ScopeError",
    "ConfigurationError",
    "MissingApiKeyError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
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


def configure(**options: Any) -> Configuration:
    """Configure the global Scope client settings.

    Sets up the global configuration that will be used by clients
    created with the `client()` function.

    Args:
        **options: Configuration options.
            api_key: API key for authentication.
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
        >>> scope_client.configure(
        ...     api_key="sk_test_123",
        ...     cache_enabled=True,
        ...     cache_ttl=600
        ... )
    """
    return ConfigurationManager.configure(**options)


def client(config: Optional[Configuration] = None, **options: Any) -> ScopeClient:
    """Create a new ScopeClient instance.

    Creates a client using the provided configuration, the global
    configuration, or a combination of both.

    Args:
        config: Optional Configuration instance to use.
        **options: Configuration options to merge with the base config.

    Returns:
        A new ScopeClient instance.

    Example:
        >>> import scope_client
        >>> scope_client.configure(api_key="sk_test_123")
        >>> client = scope_client.client()

        >>> # Or with per-client options
        >>> client = scope_client.client(cache_enabled=False)
    """
    return ScopeClient(config=config, **options)


def configuration() -> Configuration:
    """Get the current global configuration.

    Returns:
        The current global Configuration instance.

    Example:
        >>> import scope_client
        >>> scope_client.configure(api_key="sk_test_123")
        >>> config = scope_client.configuration()
        >>> print(config.api_key)
        'sk_test_123'
    """
    return ConfigurationManager.get()


def reset_configuration() -> None:
    """Reset the global configuration to defaults.

    Clears any custom configuration and resets to default values.
    Environment variables will still be loaded when a new configuration
    is created.

    Example:
        >>> import scope_client
        >>> scope_client.configure(api_key="sk_test_123")
        >>> scope_client.reset_configuration()
        >>> config = scope_client.configuration()
        >>> print(config.api_key)  # Will be None or from SCOPE_API_KEY env var
    """
    ConfigurationManager.reset()
