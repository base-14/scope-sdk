# frozen_string_literal: true

require 'faraday'

module ScopeClient
  module Middleware
    class Authentication < Faraday::Middleware
      def initialize(app, token_manager)
        super(app)
        @token_manager = token_manager
      end

      def call(env)
        env[:request_headers]['Authorization'] = "Bearer #{@token_manager.access_token}"
        env[:request_headers]['User-Agent'] = "scope-client-ruby/#{ScopeClient::VERSION}"
        env[:request_headers]['Content-Type'] = 'application/json'
        env[:request_headers]['Accept'] = 'application/json'
        @app.call(env)
      end
    end
  end
end

Faraday::Request.register_middleware(
  scope_auth: ScopeClient::Middleware::Authentication
)
