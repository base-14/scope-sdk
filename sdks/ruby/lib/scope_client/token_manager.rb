# frozen_string_literal: true

require 'monitor'
require 'faraday'
require 'json'

module ScopeClient
  class TokenManager
    include MonitorMixin

    def initialize(config)
      super()
      @config = config
      @token = nil
      @expires_at = nil
    end

    def access_token
      synchronize do
        refresh_if_needed
        @token
      end
    end

    private

    def refresh_if_needed
      return if @token && !token_expired?

      fetch_token
    end

    def token_expired?
      return true if @expires_at.nil?

      Time.now >= (@expires_at - @config.token_refresh_buffer)
    end

    def fetch_token
      credentials = @config.credentials
      response = auth_connection.post('/v1/auth/sdk-token') do |req|
        req.headers['Content-Type'] = 'application/json'
        req.headers['Accept'] = 'application/json'
        req.body = JSON.generate(
          account_id: credentials.org_id,
          key_id: credentials.api_key,
          key_secret: credentials.api_secret
        )
      end

      handle_token_response(response)
    rescue Faraday::ConnectionFailed => e
      raise TokenRefreshError, "Failed to connect to auth API: #{e.message}"
    rescue Faraday::TimeoutError => e
      raise TokenRefreshError, "Auth API request timed out: #{e.message}"
    end

    def handle_token_response(response)
      case response.status
      when 200
        parse_success_response(response.body)
      when 401
        raise InvalidCredentialsError, 'Invalid SDK credentials'
      when 403
        raise InvalidCredentialsError, 'SDK credentials are not authorized'
      else
        raise TokenRefreshError, extract_error_message(response)
      end
    end

    def parse_success_response(body)
      data = JSON.parse(body)
      @token = data['access_token']
      expires_in = data['expires_in'] || 300
      @expires_at = Time.now + expires_in
    end

    def extract_error_message(response)
      body = JSON.parse(response.body)
      body['message'] || body['error'] || "Token refresh failed (HTTP #{response.status})"
    rescue StandardError
      "Token refresh failed (HTTP #{response.status})"
    end

    def auth_connection
      @auth_connection ||= Faraday.new(url: @config.auth_api_url) do |conn|
        conn.options.timeout = @config.timeout
        conn.options.open_timeout = @config.open_timeout
        conn.adapter Faraday.default_adapter
      end
    end
  end
end
