"""Template rendering for prompt variables.

This module provides the Renderer class for substituting variables
in prompt templates.
"""

import re
from typing import Optional

from scope_client.errors import MissingVariableError, ValidationError

# Pattern to match {{variable_name}}
VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")


class Renderer:
    """Template renderer for variable substitution.

    Renders prompt templates by substituting {{variable_name}} placeholders
    with provided values. Supports strict validation of variables.

    Args:
        content: The template content with {{variable}} placeholders.
        declared_variables: Optional list of variables declared in the prompt.
            If provided, unknown variables will raise ValidationError.

    Example:
        >>> renderer = Renderer("Hello, {{name}}!")
        >>> renderer.render(name="World")
        'Hello, World!'

        >>> # With declared variables
        >>> renderer = Renderer(
        ...     "Hello, {{name}}!",
        ...     declared_variables=["name"]
        ... )
        >>> renderer.render(name="World", unknown="value")
        ValidationError: Unknown variables: unknown
    """

    def __init__(
        self,
        content: str,
        declared_variables: Optional[list[str]] = None,
    ) -> None:
        self._content = content
        self._declared_variables = (
            set(declared_variables) if declared_variables is not None else None
        )

    @property
    def content(self) -> str:
        """Get the template content."""
        return self._content

    @property
    def variables(self) -> list[str]:
        """Extract all variable names from the template.

        Returns:
            List of unique variable names found in the template.
        """
        return list(set(VARIABLE_PATTERN.findall(self._content)))

    def render(self, **values: str) -> str:
        """Render the template with provided values.

        Substitutes all {{variable}} placeholders with corresponding values
        from the provided keyword arguments.

        Args:
            **values: Keyword arguments mapping variable names to their values.
                All values will be converted to strings.

        Returns:
            Rendered template string.

        Raises:
            ValidationError: If unknown variables are provided (when declared_variables is set).
            MissingVariableError: If required variables are not provided.

        Example:
            >>> renderer = Renderer("Hello, {{name}}! You have {{count}} messages.")
            >>> renderer.render(name="Alice", count="5")
            'Hello, Alice! You have 5 messages.'
        """

        # Validate provided variables against declared variables
        self._validate_variables(values)

        # Perform substitution
        result = self._content
        for key, value in values.items():
            pattern = "{{" + key + "}}"
            result = result.replace(pattern, str(value))

        # Check for unrendered variables
        self._check_unrendered_variables(result)

        return result

    def _validate_variables(self, values: dict[str, str]) -> None:
        """Validate that all provided variables are declared.

        Args:
            values: Dictionary of variable names and values.

        Raises:
            ValidationError: If unknown variables are provided.
        """
        if self._declared_variables is None:
            return

        provided_keys = set(values.keys())
        unknown_keys = provided_keys - self._declared_variables

        if unknown_keys:
            raise ValidationError(
                f"Unknown variables: {', '.join(sorted(unknown_keys))}. "
                f"Declared variables are: {', '.join(sorted(self._declared_variables))}"
            )

    def _check_unrendered_variables(self, result: str) -> None:
        """Check for any unrendered variables in the result.

        Args:
            result: The rendered template string.

        Raises:
            MissingVariableError: If unrendered variables are found.
        """
        unrendered = VARIABLE_PATTERN.findall(result)
        if unrendered:
            raise MissingVariableError(
                missing_variables=list(set(unrendered)),
                template=self._content,
            )


def render_template(
    content: str,
    declared_variables: Optional[list[str]] = None,
    **values: str,
) -> str:
    """Convenience function to render a template.

    Args:
        content: Template content with {{variable}} placeholders.
        declared_variables: Optional list of declared variables for validation.
        **values: Keyword arguments mapping variable names to values.

    Returns:
        Rendered template string.

    Example:
        >>> render_template("Hello, {{name}}!", name="World")
        'Hello, World!'
    """
    renderer = Renderer(content, declared_variables)
    return renderer.render(**values)


def extract_variables(content: str) -> list[str]:
    """Extract variable names from a template.

    Args:
        content: Template content with {{variable}} placeholders.

    Returns:
        List of unique variable names.

    Example:
        >>> extract_variables("Hello, {{name}}! You have {{count}} messages.")
        ['name', 'count']
    """
    return list(set(VARIABLE_PATTERN.findall(content)))
