# frozen_string_literal: true

module ScopeClient
  class Client
    attr_reader :config, :connection, :cache

    def initialize(options = {})
      @config = build_config(options)
      validate_config!
      @connection = Connection.new(@config)
      @cache = Cache.new(default_ttl: @config.cache_ttl) if @config.cache_enabled
    end

    # Get prompt metadata by ID or name
    # @param prompt_id [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [Resources::Prompt] The prompt resource
    def get_prompt(prompt_id, **options)
      cache_key = "prompt:#{prompt_id}"
      fetch_with_cache(cache_key, options) do
        data = connection.get("prompts/#{prompt_id}")
        Resources::Prompt.new(data, client: self)
      end
    end

    # Get the latest version of a prompt
    # @param prompt_id [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [Resources::PromptVersion] The latest prompt version
    def get_prompt_latest(prompt_id, **options)
      cache_key = "prompt:#{prompt_id}:latest"
      fetch_with_cache(cache_key, options) do
        data = connection.get("prompts/#{prompt_id}/latest")
        Resources::PromptVersion.new(data, client: self)
      end
    end

    # Get the production version of a prompt
    # @param prompt_id [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [Resources::PromptVersion] The production prompt version
    # @raise [NoProductionVersionError] If no production version exists
    def get_prompt_production(prompt_id, **options)
      cache_key = "prompt:#{prompt_id}:production"
      fetch_with_cache(cache_key, options) do
        data = connection.get("prompts/#{prompt_id}/production")
        Resources::PromptVersion.new(data, client: self)
      end
    rescue NotFoundError
      raise NoProductionVersionError, "No production version exists for prompt #{prompt_id}"
    end

    # Get a specific version of a prompt
    # @param prompt_id [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param version_id [String] The unique identifier of the version
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [Resources::PromptVersion] The prompt version
    def get_prompt_version(prompt_id, version_id, **options)
      cache_key = "prompt:#{prompt_id}:version:#{version_id}"
      fetch_with_cache(cache_key, options) do
        data = connection.get("prompts/#{prompt_id}/versions/#{version_id}")
        Resources::PromptVersion.new(data, client: self)
      end
    end

    # List prompts with pagination and filters
    # @param params [Hash] Query parameters
    # @option params [Integer] :limit Number of items to return (max 100)
    # @option params [String] :cursor Pagination cursor
    # @option params [String] :search Search term for name and description
    # @option params [String] :tags Comma-separated list of tags
    # @option params [String] :status Filter by status (has_production_version, draft_only)
    # @option params [String] :sort_by Field to sort by (name, updated_at, created_at)
    # @option params [String] :sort_direction Sort direction (asc, desc)
    # @return [Hash] Hash with :data (array of Prompt resources) and :meta (pagination info)
    def list_prompts(**params)
      data = connection.get('prompts', params)
      {
        data: data['data'].map { |item| Resources::Prompt.new(item, client: self) },
        meta: data['meta']
      }
    end

    # Render a prompt with variable substitution
    # @param prompt_id [String] The ID (e.g., 'prompt_01ABC...') or name of the prompt.
    #   If the value starts with 'prompt_' and is a valid ULID, it's treated
    #   as an ID; otherwise, it's treated as a name.
    # @param variables [Hash] Variables to substitute in the prompt
    # @param version [Symbol, String] Version to use (:production, :latest, or specific version_id)
    # @param options [Hash] Options hash
    # @option options [Boolean] :cache Whether to use cache (default: true)
    # @option options [Integer] :cache_ttl Custom cache TTL in seconds
    # @return [String] The rendered prompt content
    def render_prompt(prompt_id, variables, version: :production, cache: true, cache_ttl: nil)
      options = { cache: cache, cache_ttl: cache_ttl }
      prompt_version = case version
                       when :production
                         get_prompt_production(prompt_id, **options)
                       when :latest
                         get_prompt_latest(prompt_id, **options)
                       else
                         get_prompt_version(prompt_id, version, **options)
                       end

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
  end
end
