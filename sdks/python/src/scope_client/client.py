"""Main ScopeClient class.

This module provides the ScopeClient class, the main entry point
for interacting with the Scope API.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

from scope_client.cache import Cache
from scope_client.configuration import Configuration, ConfigurationManager
from scope_client.connection import Connection
from scope_client.errors import NoProductionVersionError, NotFoundError
from scope_client.resources.prompt import Prompt
from scope_client.resources.prompt_version import PromptVersion

if TYPE_CHECKING:
    from scope_client.credentials import Credentials

T = TypeVar("T")


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

        >>> # Fetch a prompt
        >>> prompt = client.get_prompt("my-prompt")
        >>> print(prompt.name)

        >>> # Get production version and render
        >>> version = client.get_prompt_production("my-prompt")
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

    def get_prompt(self, prompt_id: str, **options: Any) -> Prompt:
        """Fetch a prompt by ID or name.

        Args:
            prompt_id: The ID (e.g., 'prompt_01ABC...') or name of the prompt.
                If the value starts with 'prompt_' and is a valid ULID, it's
                treated as an ID; otherwise, it's treated as a name.
            **options: Request options.
                cache: Whether to use cache (default: True if cache enabled).
                cache_ttl: Custom TTL for this request in seconds.

        Returns:
            Prompt: The fetched prompt resource.

        Raises:
            NotFoundError: If prompt not found.
            AuthenticationError: If authentication fails.
            ApiError: On other API errors.

        Example:
            >>> # Fetch by ID
            >>> prompt = client.get_prompt("prompt_01HXYZ...")
            >>> # Or fetch by name
            >>> prompt = client.get_prompt("my-prompt")
            >>> print(prompt.name)
        """
        cache_key = f"prompt:{prompt_id}"

        def fetch() -> Prompt:
            data = self._connection.get(f"prompts/{prompt_id}")
            return Prompt(data, client=self)

        return self._fetch_with_cache(cache_key, fetch, **options)

    def get_prompt_latest(self, prompt_id: str, **options: Any) -> PromptVersion:
        """Fetch the latest version of a prompt.

        Args:
            prompt_id: The ID (e.g., 'prompt_01ABC...') or name of the prompt.
                If the value starts with 'prompt_' and is a valid ULID, it's
                treated as an ID; otherwise, it's treated as a name.
            **options: Request options.
                cache: Whether to use cache (default: True if cache enabled).
                cache_ttl: Custom TTL for this request in seconds.

        Returns:
            PromptVersion: The latest version of the prompt.

        Raises:
            NotFoundError: If prompt or version not found.
            AuthenticationError: If authentication fails.
            ApiError: On other API errors.

        Example:
            >>> version = client.get_prompt_latest("my-prompt")
            >>> print(f"Latest: v{version.version_number}")
        """
        cache_key = f"prompt:{prompt_id}:latest"

        def fetch() -> PromptVersion:
            data = self._connection.get(f"prompts/{prompt_id}/latest")
            return PromptVersion(data, client=self)

        return self._fetch_with_cache(cache_key, fetch, **options)

    def get_prompt_production(self, prompt_id: str, **options: Any) -> PromptVersion:
        """Fetch the production version of a prompt.

        Args:
            prompt_id: The ID (e.g., 'prompt_01ABC...') or name of the prompt.
                If the value starts with 'prompt_' and is a valid ULID, it's
                treated as an ID; otherwise, it's treated as a name.
            **options: Request options.
                cache: Whether to use cache (default: True if cache enabled).
                cache_ttl: Custom TTL for this request in seconds.

        Returns:
            PromptVersion: The production version of the prompt.

        Raises:
            NoProductionVersionError: If no production version exists.
            NotFoundError: If prompt not found.
            AuthenticationError: If authentication fails.
            ApiError: On other API errors.

        Example:
            >>> version = client.get_prompt_production("my-prompt")
            >>> if version.is_production:
            ...     print("Got production version!")
        """
        cache_key = f"prompt:{prompt_id}:production"

        def fetch() -> PromptVersion:
            try:
                data = self._connection.get(f"prompts/{prompt_id}/production")
                return PromptVersion(data, client=self)
            except NotFoundError:
                # Convert to more specific error
                raise NoProductionVersionError(prompt_id) from None

        return self._fetch_with_cache(cache_key, fetch, **options)

    def get_prompt_version(
        self,
        prompt_id: str,
        version_id: str,
        **options: Any,
    ) -> PromptVersion:
        """Fetch a specific version of a prompt.

        Args:
            prompt_id: The ID (e.g., 'prompt_01ABC...') or name of the prompt.
                If the value starts with 'prompt_' and is a valid ULID, it's
                treated as an ID; otherwise, it's treated as a name.
            version_id: The ID of the version to fetch.
            **options: Request options.
                cache: Whether to use cache (default: True if cache enabled).
                cache_ttl: Custom TTL for this request in seconds.

        Returns:
            PromptVersion: The specified version.

        Raises:
            NotFoundError: If prompt or version not found.
            AuthenticationError: If authentication fails.
            ApiError: On other API errors.

        Example:
            >>> version = client.get_prompt_version("my-prompt", "v1")
            >>> print(version.content)
        """
        cache_key = f"prompt:{prompt_id}:version:{version_id}"

        def fetch() -> PromptVersion:
            data = self._connection.get(f"prompts/{prompt_id}/versions/{version_id}")
            return PromptVersion(data, client=self)

        return self._fetch_with_cache(cache_key, fetch, **options)

    def list_prompts(self, **params: Any) -> dict[str, Any]:
        """List all prompts.

        Args:
            **params: Query parameters for filtering/pagination.
                page: Page number (default: 1).
                per_page: Items per page (default: 20).
                sort: Sort field (e.g., 'name', 'created_at').
                order: Sort order ('asc' or 'desc').

        Returns:
            Dictionary with 'data' (list of Prompt) and 'meta' (pagination info).

        Raises:
            AuthenticationError: If authentication fails.
            ApiError: On API errors.

        Example:
            >>> result = client.list_prompts(page=1, per_page=10)
            >>> for prompt in result["data"]:
            ...     print(prompt.name)
            >>> print(f"Total: {result['meta']['total']}")
        """
        # List operations are not cached
        response = self._connection.get("prompts", params=params or None)

        # Convert data items to Prompt resources
        prompts = [Prompt(item, client=self) for item in response.get("data", [])]

        return {
            "data": prompts,
            "meta": response.get("meta", {}),
        }

    def render_prompt(
        self,
        prompt_id: str,
        variables: dict[str, str],
        version: str = "production",
        **options: Any,
    ) -> str:
        """Fetch a prompt version and render it with variables.

        Convenience method that fetches a prompt version and renders
        it with the provided variables in a single call.

        Args:
            prompt_id: The ID (e.g., 'prompt_01ABC...') or name of the prompt.
                If the value starts with 'prompt_' and is a valid ULID, it's
                treated as an ID; otherwise, it's treated as a name.
            variables: Dictionary of variable names to values.
            version: Version to use - "production", "latest", or a version ID.
            **options: Request options passed to the fetch method.

        Returns:
            Rendered prompt string.

        Raises:
            NoProductionVersionError: If version="production" and none exists.
            NotFoundError: If prompt or version not found.
            MissingVariableError: If required variables are missing.
            ValidationError: If unknown variables are provided.
            ApiError: On API errors.

        Example:
            >>> rendered = client.render_prompt(
            ...     "greeting",
            ...     {"name": "Alice", "time": "morning"},
            ...     version="production"
            ... )
            >>> print(rendered)
            'Good morning, Alice!'
        """
        # Fetch the appropriate version
        if version == "production":
            prompt_version = self.get_prompt_production(prompt_id, **options)
        elif version == "latest":
            prompt_version = self.get_prompt_latest(prompt_id, **options)
        else:
            prompt_version = self.get_prompt_version(prompt_id, version, **options)

        # Render and return
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
