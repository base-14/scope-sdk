# frozen_string_literal: true

RSpec.describe ScopeClient::Cache do
  subject(:cache) { described_class.new(default_ttl: 1) }

  describe '#fetch' do
    it 'caches and returns the value' do
      call_count = 0
      result = cache.fetch('key') do
        call_count += 1
        'value'
      end

      expect(result).to eq('value')
      expect(call_count).to eq(1)

      result2 = cache.fetch('key') do
        call_count += 1
        'other'
      end

      expect(result2).to eq('value')
      expect(call_count).to eq(1)
    end

    it 're-fetches after TTL expires' do
      call_count = 0
      cache.fetch('key') do
        call_count += 1
        'value'
      end

      sleep(1.1)

      cache.fetch('key') do
        call_count += 1
        'new_value'
      end

      expect(call_count).to eq(2)
    end

    it 'uses custom TTL when provided' do
      cache.fetch('key', ttl: 0.1) { 'value' }

      sleep(0.2)

      result = cache.get('key')
      expect(result).to be_nil
    end
  end

  describe '#get' do
    it 'returns cached value' do
      cache.set('key', 'value')

      expect(cache.get('key')).to eq('value')
    end

    it 'returns nil for missing keys' do
      expect(cache.get('missing')).to be_nil
    end

    it 'returns nil for expired keys' do
      cache.set('key', 'value', ttl: 0.1)

      sleep(0.2)

      expect(cache.get('key')).to be_nil
    end
  end

  describe '#set' do
    it 'stores value with default TTL' do
      cache.set('key', 'value')

      expect(cache.get('key')).to eq('value')
    end

    it 'stores value with custom TTL' do
      cache.set('key', 'value', ttl: 60)

      expect(cache.get('key')).to eq('value')
    end
  end

  describe '#delete' do
    it 'removes the key from cache' do
      cache.set('key', 'value')
      cache.delete('key')

      expect(cache.get('key')).to be_nil
    end
  end

  describe '#clear' do
    it 'removes all cached entries' do
      cache.set('key1', 'value1')
      cache.set('key2', 'value2')

      cache.clear

      expect(cache.get('key1')).to be_nil
      expect(cache.get('key2')).to be_nil
    end
  end

  describe '#size' do
    it 'returns the number of non-expired entries' do
      cache.set('key1', 'value1')
      cache.set('key2', 'value2')

      expect(cache.size).to eq(2)
    end
  end
end
