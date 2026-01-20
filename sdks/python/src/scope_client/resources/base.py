"""Base resource class for API responses.

This module provides the base Resource class that all API resource
classes inherit from.
"""

import json
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from scope_client.client import ScopeClient


class Resource:
    """Base class for API resource objects.

    Provides dynamic attribute access for API response data, along with
    serialization and dictionary-like access patterns.

    Args:
        data: Dictionary of resource data from API response.
        client: Optional ScopeClient reference for lazy loading related resources.

    Example:
        >>> data = {"id": "123", "name": "My Resource", "is_active": True}
        >>> resource = Resource(data)
        >>> resource.id
        '123'
        >>> resource.name
        'My Resource'
        >>> resource["id"]  # Dictionary-like access
        '123'
    """

    def __init__(
        self,
        data: dict[str, Any],
        client: Optional["ScopeClient"] = None,
    ) -> None:
        # Store raw data immutably
        self._data = dict(data)  # Make a copy
        self._client = client

        # Set known attributes directly
        for key, value in self._data.items():
            # Convert nested dicts to Resources if they look like resources
            if isinstance(value, dict) and not self._is_metadata(key):
                value = Resource(value, client=client)
            elif isinstance(value, list):
                value = [
                    Resource(item, client=client) if isinstance(item, dict) else item
                    for item in value
                ]

            # Set as attribute
            setattr(self, key, value)

    def _is_metadata(self, key: str) -> bool:
        """Check if a key represents metadata rather than a nested resource.

        Args:
            key: The key name to check.

        Returns:
            True if the key is metadata, False otherwise.
        """
        return key in {"meta", "metadata", "error", "errors", "_links"}

    @property
    def raw_data(self) -> dict[str, Any]:
        """Get the raw API response data.

        Returns:
            Dictionary of original API response data.
        """
        return dict(self._data)

    def to_dict(self) -> dict[str, Any]:
        """Convert resource to dictionary.

        Returns:
            Dictionary representation of the resource.
        """
        result: dict[str, Any] = self._serialize(self._data)
        return result

    def _serialize(self, value: Any) -> Any:
        """Serialize a value for dictionary/JSON output.

        Args:
            value: Value to serialize.

        Returns:
            Serialized value.
        """
        if isinstance(value, Resource):
            return value.to_dict()
        elif isinstance(value, dict):
            return {k: self._serialize(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._serialize(item) for item in value]
        return value

    def to_json(self, **kwargs: Any) -> str:
        """Convert resource to JSON string.

        Args:
            **kwargs: Additional arguments passed to json.dumps.

        Returns:
            JSON string representation of the resource.
        """
        return json.dumps(self.to_dict(), **kwargs)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to resource attributes.

        Args:
            key: Attribute name.

        Returns:
            Attribute value.

        Raises:
            KeyError: If attribute doesn't exist.
        """
        if key in self._data:
            return getattr(self, key)
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        """Check if resource has an attribute.

        Args:
            key: Attribute name.

        Returns:
            True if attribute exists, False otherwise.
        """
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        """Get an attribute with a default value.

        Args:
            key: Attribute name.
            default: Default value if attribute doesn't exist.

        Returns:
            Attribute value or default.
        """
        return getattr(self, key, default) if key in self._data else default

    def __repr__(self) -> str:
        """Get string representation of resource.

        Returns:
            String representation showing class name and key attributes.
        """
        class_name = self.__class__.__name__
        id_val = self._data.get("id", "")
        if id_val:
            return f"<{class_name} id={id_val!r}>"
        return f"<{class_name}>"

    def __eq__(self, other: object) -> bool:
        """Check equality with another resource.

        Args:
            other: Object to compare.

        Returns:
            True if resources are equal, False otherwise.
        """
        if not isinstance(other, Resource):
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        """Get hash value for resource.

        Returns:
            Hash based on resource ID if present.
        """
        id_val = self._data.get("id")
        if id_val:
            return hash((self.__class__.__name__, id_val))
        return hash(json.dumps(self._data, sort_keys=True))
