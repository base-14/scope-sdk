"""Prompt resource class.

This module provides the Prompt class representing a prompt resource
from the Scope API.
"""

from typing import TYPE_CHECKING, Any, Optional

from scope_client.resources.base import Resource

if TYPE_CHECKING:
    from scope_client.client import ScopeClient
    from scope_client.resources.prompt_version import PromptVersion


class Prompt(Resource):
    """Represents a prompt resource.

    A prompt is a container for prompt versions. Each prompt can have
    multiple versions, with one optionally marked as the production version.

    Args:
        data: Dictionary of prompt data from API response.
        client: Optional ScopeClient reference for fetching versions.

    Attributes:
        id: Unique identifier for the prompt.
        name: Human-readable name of the prompt.
        description: Optional description of the prompt.
        has_production_version: Whether a production version exists.
        created_at: Timestamp when prompt was created.
        updated_at: Timestamp when prompt was last updated.

    Example:
        >>> prompt = client.get_prompt("my-prompt")
        >>> prompt.name
        'My Prompt'
        >>> prompt.has_production_version
        True
        >>> version = prompt.production_version()
    """

    # Declare expected attributes for type checking
    id: str
    name: str
    description: Optional[str]
    has_production_version: bool
    created_at: str
    updated_at: str

    def __init__(
        self,
        data: dict[str, Any],
        client: Optional["ScopeClient"] = None,
    ) -> None:
        super().__init__(data, client=client)

        # Set defaults for optional fields
        if not hasattr(self, "description"):
            self.description = None
        if not hasattr(self, "has_production_version"):
            self.has_production_version = False

    def latest_version(self, **options: Any) -> "PromptVersion":
        """Fetch the latest version of this prompt.

        Args:
            **options: Options passed to client.get_prompt_version.
                cache: Whether to use cache (default: True).
                cache_ttl: Custom TTL for this request.

        Returns:
            PromptVersion: The latest version of this prompt.

        Raises:
            NotFoundError: If no versions exist.
            ApiError: On API errors.
        """
        if self._client is None:
            raise RuntimeError("Client reference required to fetch versions")

        return self._client.get_prompt_version(self.id, label="latest", **options)

    def production_version(self, **options: Any) -> "PromptVersion":
        """Fetch the production version of this prompt.

        Args:
            **options: Options passed to client.get_prompt_version.
                cache: Whether to use cache (default: True).
                cache_ttl: Custom TTL for this request.

        Returns:
            PromptVersion: The production version of this prompt.

        Raises:
            NoProductionVersionError: If no production version exists.
            NotFoundError: If prompt not found.
            ApiError: On API errors.
        """
        if self._client is None:
            raise RuntimeError("Client reference required to fetch versions")

        return self._client.get_prompt_version(self.id, **options)

    def version(self, version_id: str, **options: Any) -> "PromptVersion":
        """Fetch a specific version of this prompt.

        Args:
            version_id: The ID of the version to fetch.
            **options: Options passed to client.get_prompt_version.
                cache: Whether to use cache (default: True).
                cache_ttl: Custom TTL for this request.

        Returns:
            PromptVersion: The specified version.

        Raises:
            NotFoundError: If version not found.
            ApiError: On API errors.
        """
        if self._client is None:
            raise RuntimeError("Client reference required to fetch versions")

        return self._client.get_prompt_version(self.id, version=version_id, **options)

    def __repr__(self) -> str:
        """Get string representation of prompt.

        Returns:
            String representation showing id and name.
        """
        return f"<Prompt id={self.id!r} name={self.name!r}>"
