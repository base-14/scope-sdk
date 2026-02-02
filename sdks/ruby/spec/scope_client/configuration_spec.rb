# frozen_string_literal: true

RSpec.describe ScopeClient::Configuration do
  subject(:config) { described_class.new }

  describe '#initialize' do
    it 'sets default base_url and api_version' do
      expect(config.base_url).to be_nil # Required, no default
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

    it 'sets default credentials to nil' do
      new_config = described_class.new
      expect(new_config.credentials).to be_nil
    end

    it 'accepts custom options' do
      custom_config = described_class.new(timeout: 60, cache_ttl: 600)

      expect(custom_config.timeout).to eq(60)
      expect(custom_config.cache_ttl).to eq(600)
    end

    it 'accepts credentials option' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: 'test_org',
        api_key: 'test_key',
        api_secret: 'test_secret'
      )
      custom_config = described_class.new(credentials: credentials)

      expect(custom_config.credentials).to eq(credentials)
      expect(custom_config.credentials.org_id).to eq('test_org')
    end

    it 'sets default auth_api_url and token_refresh_buffer' do
      expect(config.auth_api_url).to be_nil # Required, no default
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

    it 'includes credentials as hash when present' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: 'test_org',
        api_key: 'test_key',
        api_secret: 'test_secret'
      )
      config_with_creds = described_class.new(credentials: credentials)
      hash = config_with_creds.to_h

      expect(hash[:credentials]).to be_a(Hash)
      expect(hash[:credentials][:org_id]).to eq('test_org')
      expect(hash[:credentials][:api_secret]).to eq('[REDACTED]')
    end
  end

  describe '#validate!' do
    context 'when credentials is nil' do
      it 'raises ConfigurationError' do
        expect { config.validate! }.to raise_error(ScopeClient::ConfigurationError, /credentials is required/)
      end
    end

    context 'when credentials is valid' do
      it 'does not raise' do
        credentials = ScopeClient::Credentials::ApiKey.new(
          org_id: 'test_org',
          api_key: 'test_key',
          api_secret: 'test_secret'
        )
        valid_config = described_class.new(
          credentials: credentials,
          base_url: 'https://api.scope.io',
          auth_api_url: 'https://auth.scope.io'
        )

        expect { valid_config.validate! }.not_to raise_error
      end
    end

    context 'when base_url is nil' do
      it 'raises ConfigurationError' do
        credentials = ScopeClient::Credentials::ApiKey.new(
          org_id: 'test_org',
          api_key: 'test_key',
          api_secret: 'test_secret'
        )
        invalid_config = described_class.new(
          credentials: credentials,
          auth_api_url: 'https://auth.scope.io'
        )

        expect { invalid_config.validate! }.to raise_error(
          ScopeClient::ConfigurationError,
          /base_url is required/
        )
      end
    end

    context 'when auth_api_url is nil' do
      it 'raises ConfigurationError' do
        credentials = ScopeClient::Credentials::ApiKey.new(
          org_id: 'test_org',
          api_key: 'test_key',
          api_secret: 'test_secret'
        )
        invalid_config = described_class.new(
          credentials: credentials,
          base_url: 'https://api.scope.io'
        )

        expect { invalid_config.validate! }.to raise_error(
          ScopeClient::ConfigurationError,
          /auth_api_url is required/
        )
      end
    end

    context 'when credentials is incomplete' do
      it 'raises ConfigurationError for missing org_id' do
        credentials = ScopeClient::Credentials::ApiKey.new(
          org_id: nil,
          api_key: 'test_key',
          api_secret: 'test_secret'
        )
        invalid_config = described_class.new(
          credentials: credentials,
          base_url: 'https://api.scope.io',
          auth_api_url: 'https://auth.scope.io'
        )

        expect { invalid_config.validate! }.to raise_error(
          ScopeClient::ConfigurationError,
          /org_id is required/
        )
      end
    end
  end
end
