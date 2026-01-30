# frozen_string_literal: true

RSpec.describe ScopeClient::Credentials::ApiKey do
  describe '#initialize' do
    it 'creates credentials with explicit values' do
      credentials = described_class.new(
        org_id: 'my-org',
        api_key: 'key_abc123',
        api_secret: 'secret_xyz'
      )

      expect(credentials.org_id).to eq('my-org')
      expect(credentials.api_key).to eq('key_abc123')
      expect(credentials.api_secret).to eq('secret_xyz')
    end

    it 'defaults values to nil' do
      credentials = described_class.new

      expect(credentials.org_id).to be_nil
      expect(credentials.api_key).to be_nil
      expect(credentials.api_secret).to be_nil
    end
  end

  describe '#auth_type' do
    it 'returns :api_key' do
      credentials = described_class.new
      expect(credentials.auth_type).to eq(:api_key)
    end
  end

  describe '#validate!' do
    context 'with all required fields' do
      it 'does not raise' do
        credentials = described_class.new(
          org_id: 'my-org',
          api_key: 'key_abc123',
          api_secret: 'secret_xyz'
        )

        expect { credentials.validate! }.not_to raise_error
      end
    end

    context 'without org_id' do
      it 'raises ConfigurationError' do
        credentials = described_class.new(
          api_key: 'key_abc123',
          api_secret: 'secret_xyz'
        )

        expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /org_id is required/)
      end
    end

    context 'with empty org_id' do
      it 'raises ConfigurationError' do
        credentials = described_class.new(
          org_id: '',
          api_key: 'key_abc123',
          api_secret: 'secret_xyz'
        )

        expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /org_id is required/)
      end
    end

    context 'without api_key' do
      it 'raises ConfigurationError' do
        credentials = described_class.new(
          org_id: 'my-org',
          api_secret: 'secret_xyz'
        )

        expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /api_key is required/)
      end
    end

    context 'without api_secret' do
      it 'raises ConfigurationError' do
        credentials = described_class.new(
          org_id: 'my-org',
          api_key: 'key_abc123'
        )

        expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /api_secret is required/)
      end
    end
  end

  describe '#to_h' do
    it 'returns hash with redacted secret' do
      credentials = described_class.new(
        org_id: 'my-org',
        api_key: 'key_abc123',
        api_secret: 'secret_xyz'
      )

      result = credentials.to_h

      expect(result[:auth_type]).to eq(:api_key)
      expect(result[:org_id]).to eq('my-org')
      expect(result[:api_key]).to eq('key_abc123')
      expect(result[:api_secret]).to eq('[REDACTED]')
    end

    it 'returns nil for api_secret when not set' do
      credentials = described_class.new(
        org_id: 'my-org',
        api_key: 'key_abc123'
      )

      result = credentials.to_h

      expect(result[:api_secret]).to be_nil
    end
  end

  describe '.from_env' do
    before do
      allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return('env-org')
      allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return('env-key')
      allow(ENV).to receive(:fetch).with('SCOPE_API_SECRET', nil).and_return('env-secret')
    end

    it 'creates credentials from environment variables' do
      credentials = described_class.from_env

      expect(credentials.org_id).to eq('env-org')
      expect(credentials.api_key).to eq('env-key')
      expect(credentials.api_secret).to eq('env-secret')
    end

    context 'when environment variables are not set' do
      before do
        allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return(nil)
        allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return(nil)
        allow(ENV).to receive(:fetch).with('SCOPE_API_SECRET', nil).and_return(nil)
      end

      it 'creates credentials with nil values' do
        credentials = described_class.from_env

        expect(credentials.org_id).to be_nil
        expect(credentials.api_key).to be_nil
        expect(credentials.api_secret).to be_nil
      end
    end
  end

  describe '#inspect' do
    it 'redacts the api_secret' do
      credentials = described_class.new(
        org_id: 'my-org',
        api_key: 'key_abc123',
        api_secret: 'secret_xyz'
      )

      result = credentials.inspect

      expect(result).to include('my-org')
      expect(result).to include('key_abc123')
      expect(result).not_to include('secret_xyz')
      expect(result).to include('[REDACTED]')
    end
  end
end

RSpec.describe ScopeClient::Credentials::Base do
  describe '#auth_type' do
    it 'raises NotImplementedError' do
      base = described_class.new
      expect { base.auth_type }.to raise_error(NotImplementedError)
    end
  end

  describe '#validate!' do
    it 'raises NotImplementedError' do
      base = described_class.new
      expect { base.validate! }.to raise_error(NotImplementedError)
    end
  end

  describe '#to_h' do
    it 'raises NotImplementedError' do
      base = described_class.new
      expect { base.to_h }.to raise_error(NotImplementedError)
    end
  end
end
