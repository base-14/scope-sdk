# frozen_string_literal: true

require 'faraday'

module ScopeClient
  module Middleware
    class Authentication < Faraday::Middleware
      def initialize(app, api_key)
        super(app)
        @api_key = api_key
      end

      def call(env)
        env[:request_headers]['Authorization'] = "Bearer #{@api_key}"
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
