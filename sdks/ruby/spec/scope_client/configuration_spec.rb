# frozen_string_literal: true

RSpec.describe ScopeClient::Configuration do
  subject(:config) { described_class.new }

  describe '#initialize' do
    it 'sets default base_url and api_version' do
      expect(config.base_url).to eq('https://api.scope.io')
      expect(config.api_version).to eq('v1')
    end

    it 'sets default timeout values' do
      expect(config.timeout).to eq(30)
      expect(config.open_timeout).to eq(10)
    end

    it 'sets default cache settings' do
      expect(config.cache_enabled).to be(true)
      expect(config.cache_ttl).to eq(300)
    end

    it 'sets default retry and telemetry settings' do
      expect(config.max_retries).to eq(3)
      expect(config.telemetry_enabled).to be(true)
    end

    it 'accepts custom options' do
      custom_config = described_class.new(timeout: 60, cache_ttl: 600)

      expect(custom_config.timeout).to eq(60)
      expect(custom_config.cache_ttl).to eq(600)
    end

    it 'loads credentials from environment' do
      allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return('env_org_id')
      allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return('env_api_key')
      allow(ENV).to receive(:fetch).with('SCOPE_API_SECRET', nil).and_return('env_api_secret')
      allow(ENV).to receive(:fetch).with('SCOPE_API_URL', anything).and_call_original
      allow(ENV).to receive(:fetch).with('SCOPE_AUTH_API_URL', anything).and_call_original
      allow(ENV).to receive(:fetch).with('SCOPE_ENVIRONMENT', anything).and_call_original
      allow(ENV).to receive(:fetch).with('SCOPE_TOKEN_REFRESH_BUFFER', anything).and_call_original

      new_config = described_class.new

      expect(new_config.org_id).to eq('env_org_id')
      expect(new_config.api_key).to eq('env_api_key')
      expect(new_config.api_secret).to eq('env_api_secret')
    end

    it 'sets default auth_api_url and token_refresh_buffer' do
      expect(config.auth_api_url).to eq('https://auth.scope.io')
      expect(config.token_refresh_buffer).to eq(60)
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
