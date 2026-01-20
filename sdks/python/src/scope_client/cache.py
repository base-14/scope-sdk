"""Thread-safe TTL cache for scope-client.

This module provides a simple in-memory cache with time-to-live expiration.
"""

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry:
    """A single cache entry with value and expiration time.

    Args:
        value: The cached value.
        expires_at: Unix timestamp when the entry expires.
    """

    value: Any
    expires_at: float

    def is_expired(self) -> bool:
        """Check if this entry has expired.

        Returns:
            True if the entry has expired, False otherwise.
        """
        return time.time() >= self.expires_at


class Cache:
    """Thread-safe TTL-based cache.

    This cache stores values with a configurable time-to-live. Expired entries
    are lazily removed when accessed or when size is queried.

    Args:
        ttl: Default time-to-live in seconds for cache entries.

    Example:
        >>> cache = Cache(ttl=300)
        >>> cache.set("key", "value")
        >>> cache.get("key")
        'value'

        >>> # Using fetch with a callable
        >>> def compute_value():
        ...     return "computed"
        >>> cache.fetch("new_key", compute_value)
        'computed'
    """

    def __init__(self, ttl: int = 300) -> None:
        self._ttl = ttl
        self._store: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    @property
    def ttl(self) -> int:
        """Get the default TTL in seconds."""
        return self._ttl

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: Cache key to look up.

        Returns:
            Cached value if found and not expired, None otherwise.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._store[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Optional TTL override in seconds. Uses default TTL if not provided.
        """
        actual_ttl = ttl if ttl is not None else self._ttl
        expires_at = time.time() + actual_ttl

        with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def fetch(
        self,
        key: str,
        func: Callable[[], T],
        ttl: Optional[int] = None,
    ) -> T:
        """Get a value from cache, computing it if not present.

        If the key is not in the cache or has expired, the provided function
        is called to compute the value, which is then cached.

        Args:
            key: Cache key.
            func: Function to call if cache misses.
            ttl: Optional TTL override in seconds.

        Returns:
            Cached or computed value.

        Example:
            >>> cache = Cache(ttl=300)
            >>> def expensive_operation():
            ...     print("Computing...")
            ...     return 42
            >>> cache.fetch("answer", expensive_operation)
            Computing...
            42
            >>> cache.fetch("answer", expensive_operation)  # No print, returns cached
            42
        """
        # Check cache first (with lock)
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value  # type: ignore[no-any-return]

        # Compute value outside the lock to avoid blocking other operations
        value = func()

        # Store the computed value
        self.set(key, value, ttl=ttl)

        return value

    def delete(self, key: str) -> bool:
        """Delete a key from the cache.

        Args:
            key: Cache key to delete.

        Returns:
            True if the key was deleted, False if it didn't exist.
        """
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        """Get the number of non-expired entries in the cache.

        This property cleans up expired entries before returning the count.

        Returns:
            Number of valid cache entries.
        """
        with self._lock:
            # Clean up expired entries
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._store.items() if current_time >= entry.expires_at
            ]
            for key in expired_keys:
                del self._store[key]

            return len(self._store)

    def has(self, key: str) -> bool:
        """Check if a key exists and is not expired.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """
        return self.get(key) is not None

    def keys(self) -> list[str]:
        """Get all non-expired keys in the cache.

        Returns:
            List of valid cache keys.
        """
        with self._lock:
            current_time = time.time()
            return [key for key, entry in self._store.items() if current_time < entry.expires_at]
