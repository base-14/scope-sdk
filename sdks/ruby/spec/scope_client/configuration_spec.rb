# frozen_string_literal: true

RSpec.describe ScopeClient::Configuration do
  subject(:config) { described_class.new }

  describe '#initialize' do
    it 'sets default values' do
      expect(config.base_url).to eq('https://api.scope.io')
      expect(config.api_version).to eq('v1')
      expect(config.timeout).to eq(30)
      expect(config.open_timeout).to eq(10)
      expect(config.cache_enabled).to be(true)
      expect(config.cache_ttl).to eq(300)
      expect(config.max_retries).to eq(3)
      expect(config.telemetry_enabled).to be(true)
    end

    it 'accepts custom options' do
      custom_config = described_class.new(timeout: 60, cache_ttl: 600)

      expect(custom_config.timeout).to eq(60)
      expect(custom_config.cache_ttl).to eq(600)
    end

    it 'loads api_key from environment' do
      allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return('env_api_key')
      allow(ENV).to receive(:fetch).with('SCOPE_API_URL', anything).and_call_original
      allow(ENV).to receive(:fetch).with('SCOPE_ENVIRONMENT', anything).and_call_original

      new_config = described_class.new

      expect(new_config.api_key).to eq('env_api_key')
    end
  end

  describe '#merge' do
    it 'returns a new configuration with merged options' do
      merged = config.merge(timeout: 120, cache_enabled: false)

      expect(merged.timeout).to eq(120)
      expect(merged.cache_enabled).to be(false)
      expect(merged.cache_ttl).to eq(config.cache_ttl)
    end

    it 'does not modify the original configuration' do
      config.merge(timeout: 120)

      expect(config.timeout).to eq(30)
    end
  end

  describe '#to_h' do
    it 'returns a hash of all configuration values' do
      hash = config.to_h

      expect(hash).to be_a(Hash)
      expect(hash[:timeout]).to eq(30)
      expect(hash[:cache_enabled]).to be(true)
    end
  end
end
