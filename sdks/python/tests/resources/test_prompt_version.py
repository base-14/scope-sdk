"""Tests for prompt and prompt version resources."""

import json
from typing import Any

import pytest

from scope_client.errors import MissingVariableError, ValidationError
from scope_client.resources import Prompt, PromptVersion, Resource


class TestResource:
    """Tests for base Resource class."""

    def test_basic_resource(self):
        """Test basic resource creation."""
        data = {"id": "123", "name": "Test"}
        resource = Resource(data)

        assert resource.id == "123"
        assert resource.name == "Test"

    def test_dictionary_access(self):
        """Test dictionary-style access."""
        data = {"id": "123", "name": "Test"}
        resource = Resource(data)

        assert resource["id"] == "123"
        assert resource["name"] == "Test"

    def test_dictionary_access_missing_key(self):
        """Test KeyError for missing key."""
        resource = Resource({"id": "123"})
        with pytest.raises(KeyError):
            _ = resource["nonexistent"]

    def test_contains(self):
        """Test 'in' operator."""
        resource = Resource({"id": "123", "name": "Test"})
        assert "id" in resource
        assert "nonexistent" not in resource

    def test_get_method(self):
        """Test get method with default."""
        resource = Resource({"id": "123"})
        assert resource.get("id") == "123"
        assert resource.get("missing") is None
        assert resource.get("missing", "default") == "default"

    def test_raw_data(self):
        """Test raw_data property."""
        data = {"id": "123", "name": "Test"}
        resource = Resource(data)
        raw = resource.raw_data

        assert raw == data
        assert raw is not data  # Should be a copy

    def test_to_dict(self):
        """Test to_dict method."""
        data = {"id": "123", "name": "Test"}
        resource = Resource(data)
        result = resource.to_dict()

        assert result == data

    def test_to_json(self):
        """Test to_json method."""
        data = {"id": "123", "name": "Test"}
        resource = Resource(data)
        result = resource.to_json()

        assert json.loads(result) == data

    def test_to_json_with_options(self):
        """Test to_json with formatting options."""
        data = {"id": "123"}
        resource = Resource(data)
        result = resource.to_json(indent=2)

        assert "  " in result  # Indented

    def test_repr(self):
        """Test string representation."""
        resource = Resource({"id": "123"})
        assert repr(resource) == "<Resource id='123'>"

    def test_repr_no_id(self):
        """Test string representation without id."""
        resource = Resource({"name": "Test"})
        assert repr(resource) == "<Resource>"

    def test_equality(self):
        """Test resource equality."""
        r1 = Resource({"id": "123"})
        r2 = Resource({"id": "123"})
        r3 = Resource({"id": "456"})

        assert r1 == r2
        assert r1 != r3

    def test_hash(self):
        """Test resource hashing."""
        r1 = Resource({"id": "123"})
        r2 = Resource({"id": "123"})

        assert hash(r1) == hash(r2)
        assert {r1, r2} == {r1}  # Same in set

    def test_nested_dict_becomes_resource(self):
        """Test nested dicts become resources."""
        data = {
            "id": "123",
            "author": {"id": "user-1", "name": "Alice"},
        }
        resource = Resource(data)

        assert isinstance(resource.author, Resource)
        assert resource.author.name == "Alice"

    def test_list_of_dicts_become_resources(self):
        """Test list of dicts become resources."""
        data = {
            "id": "123",
            "items": [
                {"id": "1", "name": "Item 1"},
                {"id": "2", "name": "Item 2"},
            ],
        }
        resource = Resource(data)

        assert len(resource.items) == 2
        assert all(isinstance(item, Resource) for item in resource.items)
        assert resource.items[0].name == "Item 1"

    def test_metadata_not_converted(self):
        """Test metadata fields are not converted to resources."""
        data = {
            "id": "123",
            "meta": {"page": 1, "total": 10},
        }
        resource = Resource(data)

        assert isinstance(resource.meta, dict)
        assert not isinstance(resource.meta, Resource)


class TestPrompt:
    """Tests for Prompt resource."""

    def test_prompt_creation(self, prompt_data: dict[str, Any]):
        """Test creating a prompt resource."""
        prompt = Prompt(prompt_data)

        assert prompt.id == "prompt-123"
        assert prompt.name == "Test Prompt"
        assert prompt.description == "A test prompt for unit tests"
        assert prompt.has_production_version is True

    def test_prompt_defaults(self):
        """Test prompt default values."""
        prompt = Prompt({"id": "123", "name": "Test"})

        assert prompt.description is None
        assert prompt.has_production_version is False

    def test_prompt_repr(self, prompt_data: dict[str, Any]):
        """Test prompt string representation."""
        prompt = Prompt(prompt_data)
        repr_str = repr(prompt)

        assert "Prompt" in repr_str
        assert "prompt-123" in repr_str
        assert "Test Prompt" in repr_str

    def test_latest_version_without_client(self, prompt_data: dict[str, Any]):
        """Test latest_version raises without client."""
        prompt = Prompt(prompt_data)
        with pytest.raises(RuntimeError, match="Client reference required"):
            prompt.latest_version()

    def test_production_version_without_client(self, prompt_data: dict[str, Any]):
        """Test production_version raises without client."""
        prompt = Prompt(prompt_data)
        with pytest.raises(RuntimeError, match="Client reference required"):
            prompt.production_version()

    def test_version_without_client(self, prompt_data: dict[str, Any]):
        """Test version raises without client."""
        prompt = Prompt(prompt_data)
        with pytest.raises(RuntimeError, match="Client reference required"):
            prompt.version("v1")


class TestPromptVersion:
    """Tests for PromptVersion resource."""

    def test_prompt_version_creation(self, prompt_version_data: dict[str, Any]):
        """Test creating a prompt version."""
        version = PromptVersion(prompt_version_data)

        assert version.id == "version-456"
        assert version.prompt_id == "prompt-123"
        assert version.version_number == 1
        assert version.content == "Hello, {{name}}! Welcome to {{app}}."
        assert version.variables == ["name", "app"]
        assert version.status == "published"
        assert version.is_production is True

    def test_prompt_version_defaults(self):
        """Test prompt version default values."""
        version = PromptVersion({"id": "v1", "prompt_id": "p1", "status": "draft"})

        assert version.variables == []
        assert version.is_production is False
        assert version.content == ""

    def test_render(self, prompt_version_data: dict[str, Any]):
        """Test rendering prompt version."""
        version = PromptVersion(prompt_version_data)
        rendered = version.render(name="Alice", app="Scope")

        assert rendered == "Hello, Alice! Welcome to Scope."

    def test_render_missing_variable(self, prompt_version_data: dict[str, Any]):
        """Test render with missing variable."""
        version = PromptVersion(prompt_version_data)

        with pytest.raises(MissingVariableError):
            version.render(name="Alice")

    def test_render_unknown_variable(self, prompt_version_data: dict[str, Any]):
        """Test render with unknown variable."""
        version = PromptVersion(prompt_version_data)

        with pytest.raises(ValidationError):
            version.render(name="Alice", app="Scope", extra="value")

    def test_is_draft(self):
        """Test is_draft property."""
        version = PromptVersion({"id": "v1", "status": "draft"})
        assert version.is_draft is True
        assert version.is_published is False
        assert version.is_archived is False

    def test_is_published(self):
        """Test is_published property."""
        version = PromptVersion({"id": "v1", "status": "published"})
        assert version.is_draft is False
        assert version.is_published is True
        assert version.is_archived is False

    def test_is_archived(self):
        """Test is_archived property."""
        version = PromptVersion({"id": "v1", "status": "archived"})
        assert version.is_draft is False
        assert version.is_published is False
        assert version.is_archived is True

    def test_repr_production(self, prompt_version_data: dict[str, Any]):
        """Test repr for production version."""
        version = PromptVersion(prompt_version_data)
        repr_str = repr(version)

        assert "PromptVersion" in repr_str
        assert "version-456" in repr_str
        assert "v1" in repr_str
        assert "(production)" in repr_str

    def test_repr_non_production(self):
        """Test repr for non-production version."""
        version = PromptVersion(
            {
                "id": "v2",
                "version_number": 2,
                "status": "draft",
                "is_production": False,
            }
        )
        repr_str = repr(version)

        assert "(production)" not in repr_str
        assert "v2" in repr_str
