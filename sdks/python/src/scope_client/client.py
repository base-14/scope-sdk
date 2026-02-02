"""Main ScopeClient class.

This module provides the ScopeClient class, the main entry point
for interacting with the Scope API.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

from scope_client.cache import Cache
from scope_client.configuration import Configuration, ConfigurationManager
from scope_client.connection import Connection
from scope_client.errors import NoProductionVersionError, NotFoundError
from scope_client.resources.prompt_version import PromptVersion

if TYPE_CHECKING:
    from scope_client.credentials import Credentials

T = TypeVar("T")

# Label constants
LABEL_PRODUCTION = "production"
LABEL_LATEST = "latest"


class ScopeClient:
    """Client for the Scope Prompt Management API.

    The ScopeClient provides methods for fetching prompts, versions,
    and rendering prompt templates with variables.

    Args:
        credentials: Optional Credentials instance for authentication.
        config: Optional Configuration instance. If not provided,
            uses the global configuration.
        base_url: Optional base URL override for the API.
        **options: Configuration options to merge with the base config.

    Example:
        >>> # Using credentials directly
        >>> from scope_client import ScopeClient, ApiKeyCredentials
        >>> credentials = ApiKeyCredentials(
        ...     org_id="my-org",
        ...     api_key="key_abc123",
        ...     api_secret="secret_xyz"
        ... )
        >>> client = ScopeClient(credentials=credentials)

        >>> # Or with credentials from environment
        >>> credentials = ApiKeyCredentials.from_env()
        >>> client = ScopeClient(credentials=credentials)

        >>> # Using global configuration
        >>> import scope_client
        >>> scope_client.configure(credentials=ApiKeyCredentials.from_env())
        >>> client = scope_client.client()

        >>> # Get production version and render
        >>> version = client.get_prompt_version("my-prompt")
        >>> rendered = version.render(name="Alice")
    """

    def __init__(
        self,
        credentials: Optional["Credentials"] = None,
        config: Optional[Configuration] = None,
        base_url: Optional[str] = None,
        **options: Any,
    ) -> None:
        # Get base configuration
        base_config = config if config is not None else ConfigurationManager.get()

        # Build options dict with credentials and base_url if provided
        merged_options: dict[str, Any] = {}
        if credentials is not None:
            merged_options["credentials"] = credentials
        if base_url is not None:
            merged_options["base_url"] = base_url
        merged_options.update(options)

        # Merge any additional options
        if merged_options:
            self._config = base_config.merge(**merged_options)
        else:
            self._config = base_config

        # Validate configuration
        self._config.validate()

        # Initialize connection
        self._connection = Connection(self._config)

        # Initialize cache if enabled
        self._cache: Optional[Cache] = None
        if self._config.cache_enabled:
            self._cache = Cache(ttl=self._config.cache_ttl)

    @property
    def config(self) -> Configuration:
        """Get the client configuration.

        Returns:
            The Configuration instance used by this client.
        """
        return self._config

    def get_prompt_version(
        self,
        name: str,
        *,
        label: Optional[str] = None,
        version: Optional[str] = None,
        **options: Any,
    ) -> PromptVersion:
        """Fetch a prompt version by name.

        Args:
            name: The name or ID of the prompt.
            label: Label to fetch - "production" (default), "latest".
            version: Specific version ID (overrides label).
            **options: Request options.
                cache: Whether to use cache (default: True if cache enabled).
                cache_ttl: Custom TTL for this request in seconds.

        Returns:
            PromptVersion: The matching prompt version.

        Raises:
            NoProductionVersionError: If label="production" and none exists.
            NotFoundError: If prompt or version not found.
            AuthenticationError: If authentication fails.
            ApiError: On other API errors.

        Example:
            >>> prompt = client.get_prompt_version("greeting")
            >>> prompt = client.get_prompt_version("greeting", label="latest")
            >>> prompt = client.get_prompt_version("greeting", version="v123")
            >>> prompt.get_metadata("model")
            >>> rendered = prompt.render(name="Alice")
        """
        cache_key, endpoint = self._resolve_prompt_version_path(name, label, version)

        def fetch() -> PromptVersion:
            try:
                data = self._connection.get(endpoint)
                return PromptVersion(data, client=self)
            except NotFoundError:
                if label is None or label == LABEL_PRODUCTION:
                    raise NoProductionVersionError(name) from None
                raise

        return self._fetch_with_cache(cache_key, fetch, **options)

    def _resolve_prompt_version_path(
        self,
        name: str,
        label: Optional[str],
        version: Optional[str],
    ) -> tuple[str, str]:
        """Resolve cache key and API endpoint for a prompt version request.

        Args:
            name: The name or ID of the prompt.
            label: Label to fetch - "production", "latest".
            version: Specific version ID (overrides label).

        Returns:
            Tuple of (cache_key, endpoint).
        """
        if version is not None:
            return (f"prompt:{name}:version:{version}", f"prompts/{name}/versions/{version}")
        elif label == LABEL_LATEST:
            return (f"prompt:{name}:latest", f"prompts/{name}/latest")
        else:
            # Default to production
            return (f"prompt:{name}:production", f"prompts/{name}/production")

    def render_prompt(
        self,
        name: str,
        variables: dict[str, str],
        label: str = LABEL_PRODUCTION,
        **options: Any,
    ) -> str:
        """Fetch a prompt version and render it with variables.

        Convenience method that fetches a prompt version and renders
        it with the provided variables in a single call.

        Args:
            name: The name or ID of the prompt.
            variables: Dictionary of variable names to values.
            label: Label to use - "production" (default) or "latest".
            **options: Request options passed to the fetch method.

        Returns:
            Rendered prompt string.

        Raises:
            NoProductionVersionError: If label="production" and none exists.
            NotFoundError: If prompt or version not found.
            MissingVariableError: If required variables are missing.
            ValidationError: If unknown variables are provided.
            ApiError: On API errors.

        Example:
            >>> rendered = client.render_prompt(
            ...     "greeting",
            ...     {"name": "Alice", "time": "morning"},
            ...     label="production"
            ... )
            >>> print(rendered)
            'Good morning, Alice!'
        """
        prompt_version = self.get_prompt_version(name, label=label, **options)
        return prompt_version.render(**variables)

    def clear_cache(self) -> None:
        """Clear all cached responses.

        Removes all entries from the cache. Has no effect if caching
        is disabled.

        Example:
            >>> client.clear_cache()
        """
        if self._cache is not None:
            self._cache.clear()

    def _fetch_with_cache(
        self,
        cache_key: str,
        fetch_func: Callable[[], T],
        **options: Any,
    ) -> T:
        """Fetch data with optional caching.

        Args:
            cache_key: Cache key for this request.
            fetch_func: Function to call if cache misses.
            **options: Options including cache control.
                cache: Whether to use cache (default: True).
                cache_ttl: Custom TTL for this entry.

        Returns:
            Fetched or cached data.
        """
        # Check if caching is enabled and requested
        use_cache = options.pop("cache", True)
        cache_ttl = options.pop("cache_ttl", None)

        if not use_cache or self._cache is None:
            return fetch_func()

        return self._cache.fetch(cache_key, fetch_func, ttl=cache_ttl)

    def close(self) -> None:
        """Close the client and release resources.

        Closes the underlying HTTP connection. The client should not
        be used after calling this method.
        """
        self._connection.close()

    def __enter__(self) -> "ScopeClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager and close client."""
        self.close()

    def __repr__(self) -> str:
        """Get string representation of client.

        Returns:
            String showing client configuration summary.
        """
        cache_status = "enabled" if self._cache else "disabled"
        return f"<ScopeClient base_url={self._config.base_url!r} cache={cache_status}>"
