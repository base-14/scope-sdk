# frozen_string_literal: true

module ScopeClient
  module Credentials
    # Base class for all credential types.
    # All credential implementations must inherit from this class
    # and implement the required methods.
    class Base
      # Returns the authentication type identifier.
      # @return [Symbol] The authentication type (e.g., :client_credentials)
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

    # Client credentials for SDK authentication.
    #
    # This is the primary authentication method for the Scope SDK,
    # using organization ID, client ID, and client secret.
    #
    # @example Create credentials explicitly
    #   credentials = ScopeClient::Credentials::ApiKey.new(
    #     org_id: 'my-org',
    #     client_id: 'key_abc123',
    #     client_secret: 'secret_xyz'
    #   )
    #
    # @example Create credentials from environment variables
    #   credentials = ScopeClient::Credentials::ApiKey.from_env
    #
    class ApiKey < Base
      attr_reader :org_id, :client_id, :client_secret

      # Creates a new ApiKey credentials instance.
      #
      # @param org_id [String, nil] Organization identifier
      # @param client_id [String, nil] Client ID for authentication
      # @param client_secret [String, nil] Client secret for authentication
      # @param api_key [String, nil] Deprecated: Use client_id instead
      # @param api_secret [String, nil] Deprecated: Use client_secret instead
      def initialize(org_id: nil, client_id: nil, client_secret: nil, api_key: nil, api_secret: nil)
        super()
        @org_id = org_id
        @client_id = resolve_credential('api_key', 'client_id', api_key, client_id)
        @client_secret = resolve_credential('api_secret', 'client_secret', api_secret, client_secret)
      end

      # Backward-compatible alias for client_id.
      # @deprecated Use {#client_id} instead
      # @return [String, nil] The client ID
      def api_key
        client_id
      end

      # Backward-compatible alias for client_secret.
      # @deprecated Use {#client_secret} instead
      # @return [String, nil] The client secret
      def api_secret
        client_secret
      end

      # Returns the authentication type identifier.
      # @return [Symbol] The symbol :client_credentials
      def auth_type
        :client_credentials
      end

      # Validates that all required credential fields are present.
      # @raise [ConfigurationError] If org_id, client_id, or client_secret is missing
      def validate!
        raise ConfigurationError, 'org_id is required' if @org_id.nil? || @org_id.to_s.empty?
        raise ConfigurationError, 'client_id is required' if @client_id.nil? || @client_id.to_s.empty?
        raise ConfigurationError, 'client_secret is required' if @client_secret.nil? || @client_secret.to_s.empty?
      end

      # Converts credentials to a hash with redacted secret.
      # @return [Hash] Hash with auth_type, org_id, client_id, and redacted client_secret
      def to_h
        {
          auth_type: auth_type,
          org_id: @org_id,
          client_id: @client_id,
          client_secret: @client_secret ? '[REDACTED]' : nil
        }
      end

      # Creates credentials from environment variables.
      #
      # Reads from:
      #   - SCOPE_ORG_ID: Organization identifier
      #   - SCOPE_CLIENT_ID: Client ID (falls back to SCOPE_API_KEY with deprecation warning)
      #   - SCOPE_CLIENT_SECRET: Client secret (falls back to SCOPE_API_SECRET with deprecation warning)
      #
      # @return [ApiKey] ApiKey instance with values from environment
      #
      # @example
      #   ENV['SCOPE_ORG_ID'] = 'my-org'
      #   ENV['SCOPE_CLIENT_ID'] = 'key_abc123'
      #   ENV['SCOPE_CLIENT_SECRET'] = 'secret_xyz'
      #   credentials = ScopeClient::Credentials::ApiKey.from_env
      #   credentials.org_id # => 'my-org'
      #
      def self.from_env
        new(
          org_id: ENV.fetch('SCOPE_ORG_ID', nil),
          client_id: resolve_env_var('SCOPE_CLIENT_ID', 'SCOPE_API_KEY'),
          client_secret: resolve_env_var('SCOPE_CLIENT_SECRET', 'SCOPE_API_SECRET')
        )
      end

      # Resolves an environment variable with fallback to a deprecated name.
      # @param new_name [String] The preferred env var name
      # @param old_name [String] The deprecated env var name
      # @return [String, nil] The resolved value
      def self.resolve_env_var(new_name, old_name)
        value = ENV.fetch(new_name, nil)
        return value if value

        value = ENV.fetch(old_name, nil)
        warn "[DEPRECATION] #{old_name} is deprecated. Use #{new_name} instead." if value
        value
      end

      private_class_method :resolve_env_var

      # Returns a string representation with redacted secret.
      # @return [String] String representation showing org_id and client_id but not secret
      def inspect
        "#<#{self.class.name} org_id=#{@org_id.inspect} client_id=#{@client_id.inspect} client_secret=[REDACTED]>"
      end

      private

      # Resolves a credential value, handling backward compatibility with deprecated names.
      # @param old_name [String] The deprecated parameter name
      # @param new_name [String] The preferred parameter name
      # @param old_value [Object, nil] The value passed via the deprecated parameter
      # @param new_value [Object, nil] The value passed via the preferred parameter
      # @return [Object, nil] The resolved value
      def resolve_credential(old_name, new_name, old_value, new_value)
        if old_value && new_value
          raise ArgumentError, "Cannot specify both #{old_name} and #{new_name}. Use #{new_name} instead."
        end

        if old_value
          warn "[DEPRECATION] #{old_name} is deprecated. Use #{new_name} instead."
          return old_value
        end

        new_value
      end
    end
  end
end
