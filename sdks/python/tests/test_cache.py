"""Tests for cache module."""

import time

from scope_client.cache import Cache, CacheEntry


class TestCacheEntry:
    """Tests for CacheEntry class."""

    def test_not_expired(self):
        """Test entry that hasn't expired."""
        entry = CacheEntry(value="test", expires_at=time.time() + 100)
        assert not entry.is_expired()

    def test_expired(self):
        """Test entry that has expired."""
        entry = CacheEntry(value="test", expires_at=time.time() - 1)
        assert entry.is_expired()

    def test_exact_expiration(self):
        """Test entry at exact expiration time."""
        entry = CacheEntry(value="test", expires_at=time.time())
        # At or past expiration time should be expired
        assert entry.is_expired()


class TestCache:
    """Tests for Cache class."""

    def test_default_ttl(self):
        """Test default TTL is 300 seconds."""
        cache = Cache()
        assert cache.ttl == 300

    def test_custom_ttl(self):
        """Test custom TTL."""
        cache = Cache(ttl=60)
        assert cache.ttl == 60

    def test_set_and_get(self):
        """Test basic set and get."""
        cache = Cache(ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        """Test get returns None for missing key."""
        cache = Cache()
        assert cache.get("nonexistent") is None

    def test_get_expired_key(self):
        """Test get returns None for expired key."""
        cache = Cache(ttl=0)  # Immediate expiration
        cache.set("key1", "value1")
        time.sleep(0.01)  # Ensure expiration
        assert cache.get("key1") is None

    def test_set_with_custom_ttl(self):
        """Test set with custom TTL."""
        cache = Cache(ttl=300)
        cache.set("short", "value", ttl=0)
        cache.set("long", "value", ttl=300)

        time.sleep(0.01)
        assert cache.get("short") is None  # Expired
        assert cache.get("long") == "value"  # Still valid

    def test_fetch_cache_hit(self):
        """Test fetch returns cached value."""
        cache = Cache(ttl=60)
        cache.set("key1", "cached_value")

        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return "computed_value"

        result = cache.fetch("key1", compute)
        assert result == "cached_value"
        assert call_count == 0  # Function not called

    def test_fetch_cache_miss(self):
        """Test fetch calls function on cache miss."""
        cache = Cache(ttl=60)

        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return "computed_value"

        result = cache.fetch("key1", compute)
        assert result == "computed_value"
        assert call_count == 1

        # Subsequent fetch should use cache
        result2 = cache.fetch("key1", compute)
        assert result2 == "computed_value"
        assert call_count == 1  # Not called again

    def test_fetch_with_custom_ttl(self):
        """Test fetch with custom TTL."""
        cache = Cache(ttl=300)

        result = cache.fetch("key1", lambda: "value", ttl=0)
        assert result == "value"

        time.sleep(0.01)
        # Should be expired, will recompute
        result2 = cache.fetch("key1", lambda: "new_value", ttl=300)
        assert result2 == "new_value"

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        cache = Cache(ttl=60)
        cache.set("key1", "value1")

        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_delete_missing_key(self):
        """Test deleting a missing key."""
        cache = Cache()
        assert cache.delete("nonexistent") is False

    def test_clear(self):
        """Test clearing all entries."""
        cache = Cache(ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size == 0

    def test_size_excludes_expired(self):
        """Test size excludes expired entries."""
        cache = Cache(ttl=60)
        cache.set("valid", "value", ttl=60)
        cache.set("expired", "value", ttl=0)

        time.sleep(0.01)
        assert cache.size == 1  # Only valid entry

    def test_has_existing_key(self):
        """Test has returns True for existing key."""
        cache = Cache(ttl=60)
        cache.set("key1", "value1")
        assert cache.has("key1") is True

    def test_has_missing_key(self):
        """Test has returns False for missing key."""
        cache = Cache()
        assert cache.has("nonexistent") is False

    def test_has_expired_key(self):
        """Test has returns False for expired key."""
        cache = Cache(ttl=0)
        cache.set("key1", "value1")
        time.sleep(0.01)
        assert cache.has("key1") is False

    def test_keys_excludes_expired(self):
        """Test keys returns only valid keys."""
        cache = Cache(ttl=60)
        cache.set("valid1", "value", ttl=60)
        cache.set("valid2", "value", ttl=60)
        cache.set("expired", "value", ttl=0)

        time.sleep(0.01)
        keys = cache.keys()
        assert "valid1" in keys
        assert "valid2" in keys
        assert "expired" not in keys

    def test_cache_different_types(self):
        """Test caching different value types."""
        cache = Cache(ttl=60)

        cache.set("string", "hello")
        cache.set("int", 42)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"key": "value"})
        cache.set("none", None)

        assert cache.get("string") == "hello"
        assert cache.get("int") == 42
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"key": "value"}
        # Note: None values are indistinguishable from missing keys with get()
