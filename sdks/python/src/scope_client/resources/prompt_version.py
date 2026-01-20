"""PromptVersion resource class.

This module provides the PromptVersion class representing a specific
version of a prompt from the Scope API.
"""

from typing import TYPE_CHECKING, Any, Optional

from scope_client.renderer import Renderer
from scope_client.resources.base import Resource

if TYPE_CHECKING:
    from scope_client.client import ScopeClient


class PromptVersion(Resource):
    """Represents a specific version of a prompt.

    A prompt version contains the actual content and variables that can
    be rendered with user-provided values.

    Args:
        data: Dictionary of version data from API response.
        client: Optional ScopeClient reference.

    Attributes:
        id: Unique identifier for this version.
        prompt_id: ID of the parent prompt.
        version_number: Sequential version number.
        content: The prompt content with variable placeholders.
        variables: List of declared variable names.
        status: Version status (draft, published, archived).
        is_production: Whether this is the production version.
        created_at: Timestamp when version was created.
        updated_at: Timestamp when version was last updated.

    Example:
        >>> version = client.get_prompt_production("my-prompt")
        >>> version.content
        'Hello, {{name}}! Welcome to {{app}}.'
        >>> version.variables
        ['name', 'app']
        >>> rendered = version.render({"name": "Alice", "app": "Scope"})
        >>> rendered
        'Hello, Alice! Welcome to Scope.'
    """

    # Declare expected attributes for type checking
    id: str
    prompt_id: str
    version_number: int
    content: str
    variables: list[str]
    status: str
    is_production: bool
    created_at: str
    updated_at: str

    def __init__(
        self,
        data: dict[str, Any],
        client: Optional["ScopeClient"] = None,
    ) -> None:
        super().__init__(data, client=client)

        # Set defaults for optional fields
        if not hasattr(self, "variables"):
            self.variables = []
        if not hasattr(self, "is_production"):
            self.is_production = False
        if not hasattr(self, "content"):
            self.content = ""

    def render(self, variables: Optional[dict[str, str]] = None) -> str:
        """Render the prompt content with provided variables.

        Substitutes all {{variable}} placeholders in the content with
        the corresponding values from the provided dictionary.

        Args:
            variables: Dictionary mapping variable names to values.
                All values are converted to strings.

        Returns:
            Rendered prompt string with all variables substituted.

        Raises:
            MissingVariableError: If required variables are not provided.
            ValidationError: If unknown variables are provided.

        Example:
            >>> version = client.get_prompt_production("greeting")
            >>> version.render({"name": "Alice", "greeting": "Hello"})
            'Hello, Alice!'
        """
        renderer = Renderer(
            content=self.content,
            declared_variables=self.variables,
        )
        return renderer.render(variables or {})

    @property
    def is_draft(self) -> bool:
        """Check if this version is a draft.

        Returns:
            True if status is 'draft', False otherwise.
        """
        return self.status == "draft"

    @property
    def is_published(self) -> bool:
        """Check if this version is published.

        Returns:
            True if status is 'published', False otherwise.
        """
        return self.status == "published"

    @property
    def is_archived(self) -> bool:
        """Check if this version is archived.

        Returns:
            True if status is 'archived', False otherwise.
        """
        return self.status == "archived"

    def __repr__(self) -> str:
        """Get string representation of prompt version.

        Returns:
            String representation showing id and version number.
        """
        prod_marker = " (production)" if self.is_production else ""
        return f"<PromptVersion id={self.id!r} v{self.version_number}{prod_marker}>"
