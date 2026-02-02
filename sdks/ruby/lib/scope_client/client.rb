# frozen_string_literal: true

module ScopeClient
  # Label constants
  LABEL_PRODUCTION = 'production'
  LABEL_LATEST = 'latest'

  class Client
    attr_reader :config, :connection, :cache

    def initialize(options = {})
      @config = build_config(options)
      validate_config!
      @connection = Connection.new(@config)
      @cache = Cache.new(default_ttl: @config.cache_ttl) if @config.cache_enabled
    end

    # Get a prompt version by name
    # @param name [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param label [String, Symbol] Label to fetch - :production (default), :latest
    # @param version [String] Specific version ID (overrides label)
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [Resources::PromptVersion] The prompt version
    # @raise [NoProductionVersionError] If label is :production and none exists
    def get_prompt_version(name, label: nil, version: nil, **options)
      cache_key, endpoint = resolve_prompt_version_path(name, label, version)
      fetch_with_cache(cache_key, options) do
        data = connection.get(endpoint)
        Resources::PromptVersion.new(data, client: self)
      end
    rescue NotFoundError
      raise NoProductionVersionError, "No production version exists for prompt #{name}" if production_label?(label)

      raise
    end

    # Render a prompt with variable substitution
    # @param name [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param variables [Hash] Variables to substitute in the prompt
    # @param label [Symbol, String] Label to use - :production (default), :latest
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [String] The rendered prompt content
    def render_prompt(name, variables, label: :production, cache: true, cache_ttl: nil)
      options = { cache: cache, cache_ttl: cache_ttl }
      prompt_version = get_prompt_version(name, label: label, **options)
      prompt_version.render(variables)
    end

    # Clear all cached data
    # @return [void]
    def clear_cache
      @cache&.clear
    end

    private

    def build_config(options)
      base_config = ScopeClient.configuration
      base_config.merge(options)
    end

    def validate_config!
      @config.validate!
    end

    def fetch_with_cache(key, options, &block)
      return yield unless @cache && options.fetch(:cache, true)

      ttl = options[:cache_ttl]
      @cache.fetch(key, ttl: ttl, &block)
    end

    def resolve_prompt_version_path(name, label, version)
      if version
        ["prompt:#{name}:version:#{version}", "prompts/#{name}/versions/#{version}"]
      elsif label.to_s == LABEL_LATEST
        ["prompt:#{name}:latest", "prompts/#{name}/latest"]
      else
        # Default to production
        ["prompt:#{name}:production", "prompts/#{name}/production"]
      end
    end

    def production_label?(label)
      label.nil? || label.to_s == LABEL_PRODUCTION
    end
  end
end
