# frozen_string_literal: true

RSpec.describe ScopeClient::Credentials do
  describe ScopeClient::Credentials::ApiKey do
    describe '#initialize' do
      it 'creates credentials with explicit values' do
        credentials = described_class.new(
          org_id: 'my-org',
          client_id: 'key_abc123',
          client_secret: 'secret_xyz'
        )

        expect(credentials.org_id).to eq('my-org')
        expect(credentials.client_id).to eq('key_abc123')
        expect(credentials.client_secret).to eq('secret_xyz')
      end

      it 'defaults values to nil' do
        credentials = described_class.new

        expect(credentials.org_id).to be_nil
        expect(credentials.client_id).to be_nil
        expect(credentials.client_secret).to be_nil
      end
    end

    describe '#auth_type' do
      it 'returns :client_credentials' do
        credentials = described_class.new
        expect(credentials.auth_type).to eq(:client_credentials)
      end
    end

    describe '#validate!' do
      context 'with all required fields' do
        it 'does not raise' do
          credentials = described_class.new(
            org_id: 'my-org',
            client_id: 'key_abc123',
            client_secret: 'secret_xyz'
          )

          expect { credentials.validate! }.not_to raise_error
        end
      end

      context 'without org_id' do
        it 'raises ConfigurationError' do
          credentials = described_class.new(
            client_id: 'key_abc123',
            client_secret: 'secret_xyz'
          )

          expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /org_id is required/)
        end
      end

      context 'with empty org_id' do
        it 'raises ConfigurationError' do
          credentials = described_class.new(
            org_id: '',
            client_id: 'key_abc123',
            client_secret: 'secret_xyz'
          )

          expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /org_id is required/)
        end
      end

      context 'without client_id' do
        it 'raises ConfigurationError' do
          credentials = described_class.new(
            org_id: 'my-org',
            client_secret: 'secret_xyz'
          )

          expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /client_id is required/)
        end
      end

      context 'without client_secret' do
        it 'raises ConfigurationError' do
          credentials = described_class.new(
            org_id: 'my-org',
            client_id: 'key_abc123'
          )

          expect { credentials.validate! }.to raise_error(ScopeClient::ConfigurationError, /client_secret is required/)
        end
      end
    end

    describe '#to_h' do
      it 'returns hash with redacted secret' do
        credentials = described_class.new(
          org_id: 'my-org',
          client_id: 'key_abc123',
          client_secret: 'secret_xyz'
        )

        result = credentials.to_h

        expect(result[:auth_type]).to eq(:client_credentials)
        expect(result[:org_id]).to eq('my-org')
        expect(result[:client_id]).to eq('key_abc123')
        expect(result[:client_secret]).to eq('[REDACTED]')
      end

      it 'returns nil for client_secret when not set' do
        credentials = described_class.new(
          org_id: 'my-org',
          client_id: 'key_abc123'
        )

        result = credentials.to_h

        expect(result[:client_secret]).to be_nil
      end
    end

    describe '.from_env' do
      before do
        allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return('env-org')
        allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_ID', nil).and_return('env-key')
        allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_SECRET', nil).and_return('env-secret')
      end

      it 'creates credentials from environment variables' do
        credentials = described_class.from_env

        expect(credentials.org_id).to eq('env-org')
        expect(credentials.client_id).to eq('env-key')
        expect(credentials.client_secret).to eq('env-secret')
      end

      context 'when environment variables are not set' do
        before do
          allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_ID', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_SECRET', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_API_SECRET', nil).and_return(nil)
        end

        it 'creates credentials with nil values' do
          credentials = described_class.from_env

          expect(credentials.org_id).to be_nil
          expect(credentials.client_id).to be_nil
          expect(credentials.client_secret).to be_nil
        end
      end
    end

    describe '#inspect' do
      it 'redacts the client_secret' do
        credentials = described_class.new(
          org_id: 'my-org',
          client_id: 'key_abc123',
          client_secret: 'secret_xyz'
        )

        result = credentials.inspect

        expect(result).to include('my-org')
        expect(result).to include('key_abc123')
        expect(result).not_to include('secret_xyz')
        expect(result).to include('[REDACTED]')
      end
    end

    describe 'backward compatibility' do
      it 'accepts old api_key kwarg with deprecation warning' do
        expect { described_class.new(org_id: 'org', api_key: 'old_key') }
          .to output(/\[DEPRECATION\] api_key is deprecated/).to_stderr

        credentials = silence_warnings { described_class.new(org_id: 'org', api_key: 'old_key') }
        expect(credentials.client_id).to eq('old_key')
      end

      it 'accepts old api_secret kwarg with deprecation warning' do
        expect { described_class.new(org_id: 'org', api_secret: 'old_secret') }
          .to output(/\[DEPRECATION\] api_secret is deprecated/).to_stderr

        credentials = silence_warnings { described_class.new(org_id: 'org', api_secret: 'old_secret') }
        expect(credentials.client_secret).to eq('old_secret')
      end

      it 'raises ArgumentError when both api_key and client_id are provided' do
        expect do
          described_class.new(org_id: 'org', api_key: 'old', client_id: 'new')
        end.to raise_error(ArgumentError, /Cannot specify both api_key and client_id/)
      end

      it 'raises ArgumentError when both api_secret and client_secret are provided' do
        expect do
          described_class.new(org_id: 'org', api_secret: 'old', client_secret: 'new')
        end.to raise_error(ArgumentError, /Cannot specify both api_secret and client_secret/)
      end

      it 'provides api_key as alias for client_id' do
        credentials = described_class.new(org_id: 'org', client_id: 'my_id')
        expect(credentials.api_key).to eq('my_id')
      end

      it 'provides api_secret as alias for client_secret' do
        credentials = described_class.new(org_id: 'org', client_secret: 'my_secret')
        expect(credentials.api_secret).to eq('my_secret')
      end

      context 'when old env vars are used via from_env' do
        before do
          allow(ENV).to receive(:fetch).with('SCOPE_ORG_ID', nil).and_return('env-org')
          allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_ID', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_API_KEY', nil).and_return('old-env-key')
          allow(ENV).to receive(:fetch).with('SCOPE_CLIENT_SECRET', nil).and_return(nil)
          allow(ENV).to receive(:fetch).with('SCOPE_API_SECRET', nil).and_return('old-env-secret')
        end

        it 'falls back to old env vars with deprecation warning' do
          expect { described_class.from_env }
            .to output(/SCOPE_API_KEY is deprecated.*SCOPE_API_SECRET is deprecated/m).to_stderr

          credentials = silence_warnings { described_class.from_env }
          expect(credentials.client_id).to eq('old-env-key')
          expect(credentials.client_secret).to eq('old-env-secret')
        end
      end
    end
  end

  describe ScopeClient::Credentials::Base do
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
end

def silence_warnings
  original_stderr = $stderr
  $stderr = StringIO.new
  result = yield
  $stderr = original_stderr
  result
end
