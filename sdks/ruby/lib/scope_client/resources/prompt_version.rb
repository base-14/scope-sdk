# frozen_string_literal: true

module ScopeClient
  module Resources
    # Prompt type constants
    PROMPT_TYPE_TEXT = 'text'
    PROMPT_TYPE_CHAT = 'chat'
    DEFAULT_PROMPT_TYPE = PROMPT_TYPE_TEXT

    class PromptVersion < Base
      def initialize(data, client: nil)
        super
        # Override the metadata accessor created by base class to handle nil
        define_singleton_method(:metadata) { @raw_data['metadata'] || {} }
      end

      # Render the prompt content with provided variables
      # @param values [Hash] Variables to substitute in the prompt
      # @return [String] The rendered prompt content
      def render(values = {})
        renderer = Renderer.new(content, variables || [])
        renderer.render(values)
      end

      # Get the prompt type
      # @return [String] The prompt type from the API, defaults to "text"
      def type
        @raw_data['prompt_type'] || DEFAULT_PROMPT_TYPE
      end

      # Get a metadata value by key
      # @param key [String, Symbol] The metadata key to retrieve
      # @param default [Object] Default value if key not found (default: nil)
      # @return [Object] The metadata value or default
      def get_metadata(key, default = nil)
        metadata.fetch(key.to_s, default)
      end

      # Check if this version is a draft
      # @return [Boolean] True if status is 'draft'
      def draft?
        status == 'draft'
      end

      # Check if this version is published
      # @return [Boolean] True if status is 'published'
      def published?
        status == 'published'
      end

      # Check if this version is archived
      # @return [Boolean] True if status is 'archived'
      def archived?
        status == 'archived'
      end

      # Alias for published?
      # @return [Boolean] True if status is 'published'
      def production?
        published?
      end
    end
  end
end
