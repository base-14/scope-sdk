# frozen_string_literal: true

module ScopeClient
  module Credentials
    # Base class for all credential types.
    # All credential implementations must inherit from this class
    # and implement the required methods.
    class Base
      # Returns the authentication type identifier.
      # @return [Symbol] The authentication type (e.g., :api_key)
      def auth_type
        raise NotImplementedError, "#{self.class} must implement #auth_type"
      end

      # Validates that all required credential fields are present.
      # @raise [ConfigurationError] If required fields are missing
      def validate!
        raise NotImplementedError, "#{self.class} must implement #validate!"
      end

      # Converts credentials to a hash representation.
      # Sensitive fields should be redacted in the output.
      # @return [Hash] Hash representation of the credentials
      def to_h
        raise NotImplementedError, "#{self.class} must implement #to_h"
      end
    end

    # API key-based credentials for SDK authentication.
    #
    # This is the primary authentication method for the Scope SDK,
    # using organization ID, API key, and API secret.
    #
    # @example Create credentials explicitly
    #   credentials = ScopeClient::Credentials::ApiKey.new(
    #     org_id: 'my-org',
    #     api_key: 'key_abc123',
    #     api_secret: 'secret_xyz'
    #   )
    #
    # @example Create credentials from environment variables
    #   credentials = ScopeClient::Credentials::ApiKey.from_env
    #
    class ApiKey < Base
      attr_reader :org_id, :api_key, :api_secret

      # Creates a new ApiKey credentials instance.
      #
      # @param org_id [String, nil] Organization identifier
      # @param api_key [String, nil] API key ID for authentication
      # @param api_secret [String, nil] API key secret for authentication
      def initialize(org_id: nil, api_key: nil, api_secret: nil)
        super()
        @org_id = org_id
        @api_key = api_key
        @api_secret = api_secret
      end

      # Returns the authentication type identifier.
      # @return [Symbol] The symbol :api_key
      def auth_type
        :api_key
      end

      # Validates that all required credential fields are present.
      # @raise [ConfigurationError] If org_id, api_key, or api_secret is missing
      def validate!
        raise ConfigurationError, 'org_id is required' if @org_id.nil? || @org_id.to_s.empty?
        raise ConfigurationError, 'api_key is required' if @api_key.nil? || @api_key.to_s.empty?
        raise ConfigurationError, 'api_secret is required' if @api_secret.nil? || @api_secret.to_s.empty?
      end

      # Converts credentials to a hash with redacted secret.
      # @return [Hash] Hash with auth_type, org_id, api_key, and redacted api_secret
      def to_h
        {
          auth_type: auth_type,
          org_id: @org_id,
          api_key: @api_key,
          api_secret: @api_secret ? '[REDACTED]' : nil
        }
      end

      # Creates credentials from environment variables.
      #
      # Reads from:
      #   - SCOPE_ORG_ID: Organization identifier
      #   - SCOPE_API_KEY: API key ID
      #   - SCOPE_API_SECRET: API key secret
      #
      # @return [ApiKey] ApiKey instance with values from environment
      #
      # @example
      #   ENV['SCOPE_ORG_ID'] = 'my-org'
      #   ENV['SCOPE_API_KEY'] = 'key_abc123'
      #   ENV['SCOPE_API_SECRET'] = 'secret_xyz'
      #   credentials = ScopeClient::Credentials::ApiKey.from_env
      #   credentials.org_id # => 'my-org'
      #
      def self.from_env
        new(
          org_id: ENV.fetch('SCOPE_ORG_ID', nil),
          api_key: ENV.fetch('SCOPE_API_KEY', nil),
          api_secret: ENV.fetch('SCOPE_API_SECRET', nil)
        )
      end

      # Returns a string representation with redacted secret.
      # @return [String] String representation showing org_id and api_key but not secret
      def inspect
        "#<#{self.class.name} org_id=#{@org_id.inspect} api_key=#{@api_key.inspect} api_secret=[REDACTED]>"
      end
    end
  end
end
