"""Configuration management for scope-client.

This module provides the Configuration class for managing SDK settings.
Configuration can be loaded from environment variables or set programmatically.
"""

import os
import threading
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from scope_client.credentials import Credentials


@dataclass(frozen=True)
class Configuration:
    """Immutable configuration for the Scope client.

    Configuration values can be set via constructor arguments or loaded
    from environment variables. Environment variables take precedence
    only when constructor arguments are not explicitly provided.

    Environment Variables:
        SCOPE_API_URL: Base URL for the API.
        SCOPE_AUTH_API_URL: Auth API URL for token exchange.
        SCOPE_ENVIRONMENT: Environment name (e.g., 'production', 'staging').
        SCOPE_TOKEN_REFRESH_BUFFER: Seconds before token expiry to refresh.

    Args:
        credentials: Credentials instance for authentication.
        base_url: Base URL for the Scope API.
        auth_api_url: Auth API URL for token exchange.
        api_version: API version string.
        timeout: Request timeout in seconds.
        open_timeout: Connection timeout in seconds.
        cache_enabled: Whether to enable response caching.
        cache_ttl: Cache time-to-live in seconds.
        max_retries: Maximum number of retry attempts.
        retry_base_delay: Base delay between retries in seconds.
        retry_max_delay: Maximum delay between retries in seconds.
        telemetry_enabled: Whether to enable telemetry.
        environment: Environment name for the client.
        token_refresh_buffer: Seconds before token expiry to refresh.

    Example:
        >>> from scope_client import ApiKeyCredentials
        >>> credentials = ApiKeyCredentials(
        ...     org_id="my-org",
        ...     api_key="key_abc123",
        ...     api_secret="secret_xyz"
        ... )
        >>> config = Configuration(credentials=credentials)

        >>> # Or load credentials from environment
        >>> credentials = ApiKeyCredentials.from_env()
        >>> config = Configuration(credentials=credentials)
    """

    credentials: Optional["Credentials"] = field(default=None)
    base_url: str = field(default="https://api.scope.io")
    auth_api_url: str = field(default="https://auth.scope.io")
    api_version: str = field(default="v1")
    timeout: int = field(default=30)
    open_timeout: int = field(default=10)
    cache_enabled: bool = field(default=True)
    cache_ttl: int = field(default=300)
    max_retries: int = field(default=3)
    retry_base_delay: float = field(default=0.5)
    retry_max_delay: float = field(default=30.0)
    telemetry_enabled: bool = field(default=True)
    environment: str = field(default="production")
    token_refresh_buffer: int = field(default=60)

    def __post_init__(self) -> None:
        """Load values from environment variables if not explicitly set."""
        # We need to use object.__setattr__ because the dataclass is frozen
        if self.base_url == "https://api.scope.io":
            env_url = os.environ.get("SCOPE_API_URL")
            if env_url:
                object.__setattr__(self, "base_url", env_url.rstrip("/"))

        if self.auth_api_url == "https://auth.scope.io":
            env_val = os.environ.get("SCOPE_AUTH_API_URL")
            if env_val:
                object.__setattr__(self, "auth_api_url", env_val.rstrip("/"))

        if self.environment == "production":
            env_environment = os.environ.get("SCOPE_ENVIRONMENT")
            if env_environment:
                object.__setattr__(self, "environment", env_environment)

        if self.token_refresh_buffer == 60:
            env_val = os.environ.get("SCOPE_TOKEN_REFRESH_BUFFER")
            if env_val:
                object.__setattr__(self, "token_refresh_buffer", int(env_val))

    def merge(self, **kwargs: Any) -> "Configuration":
        """Create a new Configuration with merged values.

        Creates a new Configuration instance with values from this instance
        overridden by any provided keyword arguments.

        Args:
            **kwargs: Configuration attributes to override.

        Returns:
            New Configuration instance with merged values.

        Example:
            >>> config = Configuration(credentials=credentials)
            >>> new_config = config.merge(timeout=60)
            >>> new_config.timeout
            60
        """
        return replace(self, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration.
        """
        result: dict[str, Any] = {
            "base_url": self.base_url,
            "auth_api_url": self.auth_api_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "open_timeout": self.open_timeout,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "max_retries": self.max_retries,
            "retry_base_delay": self.retry_base_delay,
            "retry_max_delay": self.retry_max_delay,
            "telemetry_enabled": self.telemetry_enabled,
            "environment": self.environment,
            "token_refresh_buffer": self.token_refresh_buffer,
        }
        if self.credentials is not None:
            result["credentials"] = self.credentials.to_dict()
        else:
            result["credentials"] = None
        return result

    @property
    def api_url(self) -> str:
        """Get the full API URL including version.

        Returns:
            Full API URL with version path.
        """
        return f"{self.base_url}/api/{self.api_version}"

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ConfigurationError: If credentials are not set or invalid.
        """
        from scope_client.errors import ConfigurationError

        if self.credentials is None:
            raise ConfigurationError("credentials is required")
        self.credentials.validate()


class ConfigurationManager:
    """Thread-safe global configuration manager.

    This class manages the global configuration singleton and provides
    thread-safe access to configuration state.
    """

    _lock: threading.Lock = threading.Lock()
    _configuration: Optional[Configuration] = None

    @classmethod
    def get(cls) -> Configuration:
        """Get the current global configuration.

        Returns:
            Current Configuration instance, or a new default instance
            if none has been set.
        """
        with cls._lock:
            if cls._configuration is None:
                cls._configuration = Configuration()
            return cls._configuration

    @classmethod
    def set(cls, config: Configuration) -> None:
        """Set the global configuration.

        Args:
            config: Configuration instance to use globally.
        """
        with cls._lock:
            cls._configuration = config

    @classmethod
    def reset(cls) -> None:
        """Reset the global configuration to default."""
        with cls._lock:
            cls._configuration = None

    @classmethod
    def configure(cls, **kwargs: Any) -> Configuration:
        """Configure the global client settings.

        Creates a new Configuration with the provided values and sets
        it as the global configuration.

        Args:
            **kwargs: Configuration attributes to set.

        Returns:
            The new Configuration instance.

        Example:
            >>> from scope_client import ApiKeyCredentials
            >>> ConfigurationManager.configure(
            ...     credentials=ApiKeyCredentials.from_env(),
            ...     cache_enabled=False
            ... )
        """
        with cls._lock:
            if cls._configuration is not None:
                config = cls._configuration.merge(**kwargs)
            else:
                config = Configuration(**kwargs)
            cls._configuration = config
            return config
