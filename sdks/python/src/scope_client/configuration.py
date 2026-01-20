"""Configuration management for scope-client.

This module provides the Configuration class for managing SDK settings.
Configuration can be loaded from environment variables or set programmatically.
"""

import os
import threading
from dataclasses import dataclass, field, replace
from typing import Any, Optional


@dataclass(frozen=True)
class Configuration:
    """Immutable configuration for the Scope client.

    Configuration values can be set via constructor arguments or loaded
    from environment variables. Environment variables take precedence
    only when constructor arguments are not explicitly provided.

    Environment Variables:
        SCOPE_API_KEY: API key for authentication.
        SCOPE_API_URL: Base URL for the API.
        SCOPE_ENVIRONMENT: Environment name (e.g., 'production', 'staging').

    Args:
        api_key: API key for authentication.
        base_url: Base URL for the Scope API.
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

    Example:
        >>> config = Configuration(api_key="sk_test_123")
        >>> config.api_key
        'sk_test_123'

        >>> # Load from environment
        >>> import os
        >>> os.environ["SCOPE_API_KEY"] = "sk_env_123"
        >>> config = Configuration()
        >>> config.api_key
        'sk_env_123'
    """

    api_key: Optional[str] = field(default=None)
    base_url: str = field(default="https://api.scope.io")
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

    def __post_init__(self) -> None:
        """Load values from environment variables if not explicitly set."""
        # We need to use object.__setattr__ because the dataclass is frozen
        if self.api_key is None:
            env_key = os.environ.get("SCOPE_API_KEY")
            if env_key:
                object.__setattr__(self, "api_key", env_key)

        if self.base_url == "https://api.scope.io":
            env_url = os.environ.get("SCOPE_API_URL")
            if env_url:
                object.__setattr__(self, "base_url", env_url.rstrip("/"))

        if self.environment == "production":
            env_environment = os.environ.get("SCOPE_ENVIRONMENT")
            if env_environment:
                object.__setattr__(self, "environment", env_environment)

    def merge(self, **kwargs: Any) -> "Configuration":
        """Create a new Configuration with merged values.

        Creates a new Configuration instance with values from this instance
        overridden by any provided keyword arguments.

        Args:
            **kwargs: Configuration attributes to override.

        Returns:
            New Configuration instance with merged values.

        Example:
            >>> config = Configuration(api_key="sk_test_123")
            >>> new_config = config.merge(timeout=60)
            >>> new_config.timeout
            60
            >>> new_config.api_key
            'sk_test_123'
        """
        return replace(self, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration.
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
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
        }

    @property
    def api_url(self) -> str:
        """Get the full API URL including version.

        Returns:
            Full API URL with version path.
        """
        return f"{self.base_url}/{self.api_version}"

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            MissingApiKeyError: If api_key is not set.
        """
        from scope_client.errors import MissingApiKeyError

        if not self.api_key:
            raise MissingApiKeyError()


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
            >>> ConfigurationManager.configure(
            ...     api_key="sk_test_123",
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
