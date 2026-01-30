# frozen_string_literal: true

require_relative 'scope_client/version'
require_relative 'scope_client/errors'
require_relative 'scope_client/credentials'
require_relative 'scope_client/configuration'
require_relative 'scope_client/token_manager'
require_relative 'scope_client/cache'
require_relative 'scope_client/renderer'
require_relative 'scope_client/middleware/authentication'
require_relative 'scope_client/middleware/telemetry'
require_relative 'scope_client/connection'
require_relative 'scope_client/resources/base'
require_relative 'scope_client/resources/prompt'
require_relative 'scope_client/resources/prompt_version'
require_relative 'scope_client/client'

module ScopeClient
  class << self
    attr_writer :configuration

    def configuration
      @configuration ||= Configuration.new
    end

    def configure
      yield(configuration)
    end

    def client(options = {})
      Client.new(options)
    end

    def reset_configuration!
      @configuration = Configuration.new
    end
  end
end
