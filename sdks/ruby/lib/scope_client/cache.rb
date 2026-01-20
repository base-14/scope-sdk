# frozen_string_literal: true

require 'monitor'

module ScopeClient
  class Cache
    include MonitorMixin

    CacheEntry = Struct.new(:value, :expires_at) do
      def expired?
        Time.now > expires_at
      end
    end

    def initialize(default_ttl: 300)
      super()
      @store = {}
      @default_ttl = default_ttl
    end

    def fetch(key, ttl: nil)
      synchronize do
        entry = @store[key]

        return entry.value if entry && !entry.expired?

        value = yield
        set(key, value, ttl: ttl)
        value
      end
    end

    def get(key)
      synchronize do
        entry = @store[key]
        return nil unless entry
        return nil if entry.expired?

        entry.value
      end
    end

    def set(key, value, ttl: nil)
      synchronize do
        ttl ||= @default_ttl
        expires_at = Time.now + ttl
        @store[key] = CacheEntry.new(value, expires_at)
        value
      end
    end

    def delete(key)
      synchronize do
        @store.delete(key)
      end
    end

    def clear
      synchronize do
        @store.clear
      end
    end

    def size
      synchronize do
        cleanup_expired
        @store.size
      end
    end

    private

    def cleanup_expired
      @store.delete_if { |_, entry| entry.expired? }
    end
  end
end
