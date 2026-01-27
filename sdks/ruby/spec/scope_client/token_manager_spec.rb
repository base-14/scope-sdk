# frozen_string_literal: true

RSpec.describe ScopeClient::TokenManager do
  subject(:token_manager) { described_class.new(config) }

  let(:config) do
    ScopeClient::Configuration.new(
      org_id: 'test_org',
      api_key: 'test_key',
      api_secret: 'test_secret',
      auth_api_url: 'https://auth.scope.io',
      token_refresh_buffer: 60
    )
  end

  describe '#access_token' do
    context 'when no token is cached' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .with(
            body: { account_id: 'test_org', key_id: 'test_key', key_secret: 'test_secret' }.to_json
          )
          .to_return(
            status: 200,
            body: { access_token: 'jwt_token_123', expires_in: 3600 }.to_json,
            headers: { 'Content-Type' => 'application/json' }
          )
      end

      it 'fetches a new token from the auth API' do
        expect(token_manager.access_token).to eq('jwt_token_123')
      end

      it 'caches the token for subsequent calls' do
        token_manager.access_token
        token_manager.access_token

        expect(WebMock).to have_requested(:post, 'https://auth.scope.io/v1/auth/sdk-token').once
      end
    end

    context 'when token is expired' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_return(
            status: 200,
            body: { access_token: 'new_token', expires_in: 1 }.to_json,
            headers: { 'Content-Type' => 'application/json' }
          )
      end

      it 'refreshes the token when expired' do
        # First call gets initial token
        token_manager.access_token

        # Wait for token to expire (token_refresh_buffer is 60, expires_in is 1)
        # Since 1 - 60 < 0, the token is immediately considered expired
        sleep(0.1)

        # Second call should refresh
        token_manager.access_token

        expect(WebMock).to have_requested(:post, 'https://auth.scope.io/v1/auth/sdk-token').twice
      end
    end

    context 'when auth API returns 401' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_return(status: 401, body: { message: 'Invalid credentials' }.to_json)
      end

      it 'raises InvalidCredentialsError' do
        expect { token_manager.access_token }.to raise_error(ScopeClient::InvalidCredentialsError)
      end
    end

    context 'when auth API returns 403' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_return(status: 403, body: { message: 'Not authorized' }.to_json)
      end

      it 'raises InvalidCredentialsError' do
        expect { token_manager.access_token }.to raise_error(ScopeClient::InvalidCredentialsError)
      end
    end

    context 'when auth API returns 500' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_return(status: 500, body: { message: 'Server error' }.to_json)
      end

      it 'raises TokenRefreshError' do
        expect { token_manager.access_token }.to raise_error(ScopeClient::TokenRefreshError)
      end
    end

    context 'when connection fails' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_raise(Faraday::ConnectionFailed.new('Connection refused'))
      end

      it 'raises TokenRefreshError with connection message' do
        expect { token_manager.access_token }
          .to raise_error(ScopeClient::TokenRefreshError, /Failed to connect/)
      end
    end

    context 'when request times out' do
      before do
        stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
          .to_raise(Faraday::TimeoutError.new('Timeout'))
      end

      it 'raises TokenRefreshError with timeout message' do
        expect { token_manager.access_token }
          .to raise_error(ScopeClient::TokenRefreshError, /timed out/)
      end
    end
  end
end
