# frozen_string_literal: true

module ScopeClient
  module Resources
    class PromptVersion < Base
      def render(values = {})
        renderer = Renderer.new(content, variables || [])
        renderer.render(values)
      end

      def draft?
        status == 'draft'
      end

      def published?
        status == 'published'
      end

      def archived?
        status == 'archived'
      end

      def production?
        published?
      end
    end
  end
end
