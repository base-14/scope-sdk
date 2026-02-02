"""Tests for renderer module."""

import pytest

from scope_client.errors import MissingVariableError, ValidationError
from scope_client.renderer import Renderer, extract_variables, render_template


class TestRenderer:
    """Tests for Renderer class."""

    def test_simple_render(self):
        """Test simple variable substitution."""
        renderer = Renderer("Hello, {{name}}!")
        result = renderer.render(name="World")
        assert result == "Hello, World!"

    def test_multiple_variables(self):
        """Test multiple variable substitution."""
        renderer = Renderer("Hello, {{name}}! Welcome to {{app}}.")
        result = renderer.render(name="Alice", app="Scope")
        assert result == "Hello, Alice! Welcome to Scope."

    def test_repeated_variable(self):
        """Test same variable used multiple times."""
        renderer = Renderer("{{name}} says hello. {{name}} is here.")
        result = renderer.render(name="Bob")
        assert result == "Bob says hello. Bob is here."

    def test_no_variables(self):
        """Test content with no variables."""
        renderer = Renderer("Hello, World!")
        result = renderer.render()
        assert result == "Hello, World!"

    def test_empty_values(self):
        """Test rendering with empty string value."""
        renderer = Renderer("Hello, {{name}}!")
        result = renderer.render(name="")
        assert result == "Hello, !"

    def test_numeric_values(self):
        """Test rendering with numeric values."""
        renderer = Renderer("You have {{count}} messages.")
        result = renderer.render(count="42")
        assert result == "You have 42 messages."

    def test_variables_property(self):
        """Test extracting variables from template."""
        renderer = Renderer("Hello, {{name}}! You have {{count}} from {{sender}}.")
        variables = renderer.variables
        assert set(variables) == {"name", "count", "sender"}

    def test_variables_deduplication(self):
        """Test that duplicate variables are deduplicated."""
        renderer = Renderer("{{name}} and {{name}} again.")
        variables = renderer.variables
        assert variables.count("name") == 1

    def test_content_property(self):
        """Test content property."""
        template = "Hello, {{name}}!"
        renderer = Renderer(template)
        assert renderer.content == template

    def test_render_with_no_args(self):
        """Test render with no arguments."""
        renderer = Renderer("Hello, World!")
        result = renderer.render()
        assert result == "Hello, World!"

    def test_missing_variable_error(self):
        """Test error when required variable is missing."""
        renderer = Renderer("Hello, {{name}}!")
        with pytest.raises(MissingVariableError) as exc_info:
            renderer.render()

        assert "name" in exc_info.value.missing_variables

    def test_multiple_missing_variables(self):
        """Test error lists all missing variables."""
        renderer = Renderer("{{greeting}}, {{name}}!")
        with pytest.raises(MissingVariableError) as exc_info:
            renderer.render()

        assert set(exc_info.value.missing_variables) == {"greeting", "name"}

    def test_partial_missing_variables(self):
        """Test error when some variables are missing."""
        renderer = Renderer("{{greeting}}, {{name}}!")
        with pytest.raises(MissingVariableError) as exc_info:
            renderer.render(greeting="Hello")

        assert "name" in exc_info.value.missing_variables
        assert "greeting" not in exc_info.value.missing_variables


class TestRendererWithDeclaredVariables:
    """Tests for Renderer with declared variables validation."""

    def test_valid_declared_variables(self):
        """Test render with all declared variables provided."""
        renderer = Renderer(
            "Hello, {{name}}!",
            declared_variables=["name"],
        )
        result = renderer.render(name="World")
        assert result == "Hello, World!"

    def test_unknown_variable_error(self):
        """Test error when unknown variable is provided."""
        renderer = Renderer(
            "Hello, {{name}}!",
            declared_variables=["name"],
        )
        with pytest.raises(ValidationError) as exc_info:
            renderer.render(name="World", unknown="value")

        assert "Unknown variables" in str(exc_info.value)
        assert "unknown" in str(exc_info.value)

    def test_multiple_unknown_variables(self):
        """Test error lists all unknown variables."""
        renderer = Renderer(
            "Hello, {{name}}!",
            declared_variables=["name"],
        )
        with pytest.raises(ValidationError) as exc_info:
            renderer.render(name="World", foo="1", bar="2")

        error_str = str(exc_info.value)
        assert "foo" in error_str
        assert "bar" in error_str

    def test_empty_declared_variables(self):
        """Test with empty declared variables list."""
        renderer = Renderer("Hello!", declared_variables=[])
        # Should fail because "name" is not declared
        with pytest.raises(ValidationError):
            renderer.render(name="World")

    def test_extra_declared_variables_ok(self):
        """Test that having declared but unused variables is OK."""
        renderer = Renderer(
            "Hello, {{name}}!",
            declared_variables=["name", "unused"],
        )
        result = renderer.render(name="World")
        assert result == "Hello, World!"


class TestRenderTemplate:
    """Tests for render_template convenience function."""

    def test_basic_render(self):
        """Test basic template rendering."""
        result = render_template("Hello, {{name}}!", name="World")
        assert result == "Hello, World!"

    def test_with_declared_variables(self):
        """Test with declared variables."""
        result = render_template(
            "Hello, {{name}}!",
            declared_variables=["name"],
            name="World",
        )
        assert result == "Hello, World!"

    def test_no_values(self):
        """Test with no values."""
        result = render_template("Hello, World!")
        assert result == "Hello, World!"


class TestExtractVariables:
    """Tests for extract_variables function."""

    def test_basic_extraction(self):
        """Test basic variable extraction."""
        variables = extract_variables("Hello, {{name}}!")
        assert variables == ["name"]

    def test_multiple_variables(self):
        """Test extracting multiple variables."""
        variables = extract_variables("{{greeting}}, {{name}}!")
        assert set(variables) == {"greeting", "name"}

    def test_no_variables(self):
        """Test extracting from content with no variables."""
        variables = extract_variables("Hello, World!")
        assert variables == []

    def test_duplicate_variables(self):
        """Test that duplicates are removed."""
        variables = extract_variables("{{name}} and {{name}}")
        assert variables.count("name") == 1

    def test_underscore_variables(self):
        """Test variables with underscores."""
        variables = extract_variables("{{user_name}} {{first_name}}")
        assert set(variables) == {"user_name", "first_name"}

    def test_numeric_variables(self):
        """Test variables with numbers."""
        variables = extract_variables("{{var1}} {{var2}}")
        assert set(variables) == {"var1", "var2"}
