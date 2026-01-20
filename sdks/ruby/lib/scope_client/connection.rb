# frozen_string_literal: true

require 'faraday'
require 'faraday/retry'
require 'json'

module ScopeClient
  class Connection
    attr_reader :config

    def initialize(config)
      @config = config
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
        conn.use Middleware::Authentication, config.api_key
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
      case response.status
      when 200..299
        response.body
      when 401
        raise AuthenticationError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      when 403
        raise AuthorizationError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      when 404
        raise NotFoundError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      when 409
        raise ConflictError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      when 429
        raise RateLimitError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      when 500..599
        raise ServerError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      else
        raise ApiError.new(
          error_message(response),
          http_status: response.status,
          http_body: response.body
        )
      end
    end

    def error_message(response)
      return 'Unknown error' unless response.body.is_a?(Hash)

      response.body['message'] || response.body['error'] || 'Unknown error'
    end
  end
end
