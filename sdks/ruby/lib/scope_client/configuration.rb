# frozen_string_literal: true

require 'monitor'

module ScopeClient
  class Configuration
    include MonitorMixin

    DEFAULTS = {
      org_id: nil,
      api_key: nil,
      api_secret: nil,
      base_url: 'https://api.scope.io',
      auth_api_url: 'https://auth.scope.io',
      api_version: 'v1',
      timeout: 30,
      open_timeout: 10,
      cache_enabled: true,
      cache_ttl: 300,
      max_retries: 3,
      retry_base_delay: 0.5,
      retry_max_delay: 30,
      logger: nil,
      telemetry_enabled: true,
      environment: :production,
      token_refresh_buffer: 60
    }.freeze

    ATTRIBUTES = DEFAULTS.keys.freeze

    attr_accessor(*ATTRIBUTES)

    def initialize(options = {})
      super()
      DEFAULTS.each do |key, default_value|
        instance_variable_set(:"@#{key}", options.fetch(key, default_value))
      end
      load_from_environment!
    end

    def merge(options)
      synchronize do
        new_config = dup
        options.each do |key, value|
          new_config.public_send(:"#{key}=", value) if ATTRIBUTES.include?(key)
        end
        new_config
      end
    end

    def to_h
      synchronize do
        ATTRIBUTES.each_with_object({}) do |attr, hash|
          hash[attr] = public_send(attr)
        end
      end
    end

    def validate!
      raise ConfigurationError, 'org_id is required' if @org_id.nil? || @org_id.to_s.empty?
      raise ConfigurationError, 'api_key is required' if @api_key.nil? || @api_key.to_s.empty?
      raise ConfigurationError, 'api_secret is required' if @api_secret.nil? || @api_secret.to_s.empty?
    end

    private

    def load_from_environment!
      @org_id ||= ENV.fetch('SCOPE_ORG_ID', nil)
      @api_key ||= ENV.fetch('SCOPE_API_KEY', nil)
      @api_secret ||= ENV.fetch('SCOPE_API_SECRET', nil)
      @base_url = ENV.fetch('SCOPE_API_URL', @base_url)
      @auth_api_url = ENV.fetch('SCOPE_AUTH_API_URL', @auth_api_url)
      @environment = ENV.fetch('SCOPE_ENVIRONMENT', @environment.to_s).to_sym
      @token_refresh_buffer = ENV.fetch('SCOPE_TOKEN_REFRESH_BUFFER', @token_refresh_buffer).to_i
    end
  end
end
