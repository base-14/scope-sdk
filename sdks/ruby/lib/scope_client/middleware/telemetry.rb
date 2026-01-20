# frozen_string_literal: true

require 'faraday'
require 'securerandom'

module ScopeClient
  module Middleware
    class Telemetry < Faraday::Middleware
      class << self
        attr_accessor :on_request, :on_response, :on_error
      end

      def call(env)
        start_time = Time.now
        request_id = SecureRandom.uuid

        notify_request(env, request_id)

        @app.call(env).on_complete do |response_env|
          duration = Time.now - start_time
          notify_response(response_env, request_id, duration)
        end
      rescue StandardError => e
        duration = Time.now - start_time
        notify_error(e, env, request_id, duration)
        raise
      end

      private

      def notify_request(env, request_id)
        return unless self.class.on_request

        self.class.on_request.call({
                                     request_id: request_id,
                                     method: env[:method],
                                     url: env[:url].to_s,
                                     timestamp: Time.now
                                   })
      end

      def notify_response(env, request_id, duration)
        return unless self.class.on_response

        self.class.on_response.call({
                                      request_id: request_id,
                                      status: env[:status],
                                      duration: duration,
                                      timestamp: Time.now
                                    })
      end

      def notify_error(error, env, request_id, duration)
        return unless self.class.on_error

        self.class.on_error.call({
                                   request_id: request_id,
                                   error: error,
                                   method: env[:method],
                                   url: env[:url].to_s,
                                   duration: duration,
                                   timestamp: Time.now
                                 })
      end
    end
  end
end

Faraday::Middleware.register_middleware(
  scope_telemetry: ScopeClient::Middleware::Telemetry
)
