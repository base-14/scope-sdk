# frozen_string_literal: true

module ScopeClient
  module Resources
    class Prompt < Base
      def latest_version
        @client.get_prompt_latest(prompt_id)
      end

      def production_version
        @client.get_prompt_production(prompt_id)
      end

      def version(version_id)
        @client.get_prompt_version(prompt_id, version_id)
      end

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
