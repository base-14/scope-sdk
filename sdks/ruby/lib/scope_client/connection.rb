# frozen_string_literal: true

require 'faraday'
require 'faraday/retry'
require 'json'

module ScopeClient
  class Connection
    STATUS_ERROR_MAP = {
      401 => AuthenticationError,
      403 => AuthorizationError,
      404 => NotFoundError,
      409 => ConflictError,
      429 => RateLimitError
    }.freeze

    attr_reader :config

    def initialize(config)
      @config = config
      @token_manager = TokenManager.new(config)
      @connection = build_connection
    end

    def get(path, params = {}, headers = {})
      request(:get, path, params, headers)
    end

    def request(method, path, params = {}, headers = {})
      response = @connection.public_send(method, path) do |req|
        req.headers.merge!(headers)
        if method == :get
          req.params = params
        else
          req.body = JSON.generate(params) unless params.empty?
        end
      end

      handle_response(response)
    rescue Faraday::ConnectionFailed => e
      raise ConnectionError, "Connection failed: #{e.message}"
    rescue Faraday::TimeoutError => e
      raise TimeoutError, "Request timed out: #{e.message}"
    end

    private

    def build_connection
      Faraday.new(url: base_url) do |conn|
        conn.use Middleware::Authentication, @token_manager
        conn.use Middleware::Telemetry if config.telemetry_enabled

        conn.request :retry, retry_options

        conn.response :json, content_type: /\bjson$/

        conn.options.timeout = config.timeout
        conn.options.open_timeout = config.open_timeout

        conn.adapter Faraday.default_adapter
      end
    end

    def base_url
      "#{config.base_url}/api/#{config.api_version}"
    end

    def retry_options
      {
        max: config.max_retries,
        interval: config.retry_base_delay,
        interval_randomness: 0.5,
        backoff_factor: 2,
        max_interval: config.retry_max_delay,
        retry_statuses: [429, 500, 502, 503, 504],
        retry_if: ->(_env, _exception) { retriable_request? }
      }
    end

    def retriable_request?
      true
    end

    def handle_response(response)
      return response.body if response.status.between?(200, 299)

      raise_error_for_status(response)
    end

    def raise_error_for_status(response)
      error_class = error_class_for_status(response.status)
      raise error_class.new(
        error_message(response),
        http_status: response.status,
        http_body: response.body
      )
    end

    def error_class_for_status(status)
      return STATUS_ERROR_MAP[status] if STATUS_ERROR_MAP.key?(status)
      return ServerError if status >= 500

      ApiError
    end

    def error_message(response)
      return 'Unknown error' unless response.body.is_a?(Hash)

      response.body['message'] || response.body['error'] || 'Unknown error'
    end
  end
end
