# frozen_string_literal: true

RSpec.describe ScopeClient::Error do
  describe '#initialize' do
    it 'accepts message' do
      error = described_class.new('Something went wrong')

      expect(error.message).to include('Something went wrong')
    end

    it 'accepts http_status parameter' do
      error = described_class.new('Error', http_status: 500)

      expect(error.http_status).to eq(500)
      expect(error.message).to include('HTTP 500')
    end

    it 'accepts http_body parameter' do
      error = described_class.new('Error', http_body: { 'error' => 'Internal error' })

      expect(error.http_body).to eq({ 'error' => 'Internal error' })
    end

    it 'accepts error_code and request_id parameters' do
      error = described_class.new('Error', error_code: 'INTERNAL_ERROR', request_id: 'req_123')

      expect(error.error_code).to eq('INTERNAL_ERROR')
      expect(error.request_id).to eq('req_123')
    end
  end

  describe '#to_s' do
    it 'includes message and metadata' do
      error = described_class.new(
        'Error occurred',
        http_status: 400,
        error_code: 'BAD_REQUEST',
        request_id: 'req_456'
      )

      result = error.to_s

      expect(result).to include('Error occurred')
      expect(result).to include('HTTP 400')
    end

    it 'includes error code and request_id in output' do
      error = described_class.new('Error', error_code: 'BAD_REQUEST', request_id: 'req_456')

      expect(error.to_s).to include('BAD_REQUEST')
      expect(error.to_s).to include('req_456')
    end

    it 'omits nil values' do
      error = described_class.new('Simple error')

      expect(error.to_s).to eq('Simple error')
    end
  end

  describe ScopeClient::MissingApiKeyError do
    it 'has a descriptive message' do
      error = described_class.new

      expect(error.message).to include('API key is required')
      expect(error.message).to include('SCOPE_API_KEY')
    end

    it 'inherits from ConfigurationError' do
      expect(described_class.superclass).to eq(ScopeClient::ConfigurationError)
    end
  end

  describe 'inheritance hierarchy' do
    it 'has ConfigurationError inheriting from Error' do
      expect(ScopeClient::ConfigurationError.superclass).to eq(described_class)
    end

    it 'has ApiError inheriting from Error' do
      expect(ScopeClient::ApiError.superclass).to eq(described_class)
    end

    it 'has ResourceError inheriting from Error' do
      expect(ScopeClient::ResourceError.superclass).to eq(described_class)
    end

    it 'has HTTP error classes inheriting from ApiError' do
      expect(ScopeClient::AuthenticationError.superclass).to eq(ScopeClient::ApiError)
      expect(ScopeClient::AuthorizationError.superclass).to eq(ScopeClient::ApiError)
      expect(ScopeClient::NotFoundError.superclass).to eq(ScopeClient::ApiError)
      expect(ScopeClient::RateLimitError.superclass).to eq(ScopeClient::ApiError)
      expect(ScopeClient::ServerError.superclass).to eq(ScopeClient::ApiError)
    end

    it 'has connection errors inheriting from ApiError' do
      expect(ScopeClient::ConnectionError.superclass).to eq(ScopeClient::ApiError)
      expect(ScopeClient::TimeoutError.superclass).to eq(ScopeClient::ConnectionError)
    end

    it 'has resource-specific errors inheriting from ResourceError' do
      expect(ScopeClient::ValidationError.superclass).to eq(ScopeClient::ResourceError)
      expect(ScopeClient::RenderError.superclass).to eq(ScopeClient::ResourceError)
      expect(ScopeClient::MissingVariableError.superclass).to eq(ScopeClient::RenderError)
      expect(ScopeClient::NoProductionVersionError.superclass).to eq(ScopeClient::ResourceError)
    end
  end
end
