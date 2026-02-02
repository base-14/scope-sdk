# frozen_string_literal: true

module ScopeClient
  module Resources
    class Prompt < Base
      # Fetch the latest version of this prompt
      # @return [PromptVersion] The latest version
      def latest_version
        @client.get_prompt_version(prompt_id, label: :latest)
      end

      # Fetch the production version of this prompt
      # @return [PromptVersion] The production version
      # @raise [NoProductionVersionError] If no production version exists
      def production_version
        @client.get_prompt_version(prompt_id)
      end

      # Fetch a specific version of this prompt
      # @param version_id [String] The ID of the version to fetch
      # @return [PromptVersion] The specified version
      def version(version_id)
        @client.get_prompt_version(prompt_id, version: version_id)
      end

      # Check if this prompt has a production version
      # @return [Boolean] True if production version exists
      def production_version?
        !production_version_number.nil?
      end

      private

      def production_version_number
        @raw_data['production_version']
      end
    end
  end
end
