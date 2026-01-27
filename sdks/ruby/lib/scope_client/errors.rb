# frozen_string_literal: true

module ScopeClient
  # Base error class for all Scope SDK errors
  class Error < StandardError
    attr_reader :http_status, :http_body, :error_code, :request_id

    def initialize(message = nil, http_status: nil, http_body: nil, error_code: nil, request_id: nil)
      @http_status = http_status
      @http_body = http_body
      @error_code = error_code
      @request_id = request_id
      super(message)
    end

    def to_s
      parts = [super]
      parts << "(HTTP #{http_status})" if http_status
      parts << "[#{error_code}]" if error_code
      parts << "Request ID: #{request_id}" if request_id
      parts.join(' ')
    end
  end

  # Configuration errors
  class ConfigurationError < Error; end

  class MissingApiKeyError < ConfigurationError
    def initialize
      super('API key is required. Set SCOPE_API_KEY or pass api_key to client.')
    end
  end

  # HTTP/API errors
  class ApiError < Error; end
  class AuthenticationError < ApiError; end
  class TokenRefreshError < AuthenticationError; end
  class InvalidCredentialsError < AuthenticationError; end
  class AuthorizationError < ApiError; end
  class NotFoundError < ApiError; end
  class ConflictError < ApiError; end
  class RateLimitError < ApiError; end
  class ServerError < ApiError; end
  class ConnectionError < ApiError; end
  class TimeoutError < ConnectionError; end

  # Resource errors
  class ResourceError < Error; end
  class ValidationError < ResourceError; end
  class RenderError < ResourceError; end
  class MissingVariableError < RenderError; end
  class NoProductionVersionError < ResourceError; end
end
