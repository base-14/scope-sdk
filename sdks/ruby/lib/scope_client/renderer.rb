# frozen_string_literal: true

module ScopeClient
  class Renderer
    VARIABLE_PATTERN = /\{\{(\w+)\}\}/.freeze

    def initialize(content, variables = [])
      @content = content
      @declared_variables = variables
    end

    def render(values = {})
      validate_variables!(values)

      result = @content.dup
      values.each do |key, value|
        result.gsub!(/\{\{#{key}\}\}/, value.to_s)
      end

      check_unrendered_variables!(result)
      result
    end

    def extract_variables
      @content.scan(VARIABLE_PATTERN).flatten.uniq
    end

    private

    def validate_variables!(values)
      provided_keys = values.keys.map(&:to_s)
      declared = @declared_variables.map(&:to_s)

      extra_keys = provided_keys - declared
      return if extra_keys.empty?

      raise ValidationError, "Unknown variables: #{extra_keys.join(', ')}"
    end

    def check_unrendered_variables!(result)
      unrendered = result.scan(VARIABLE_PATTERN).flatten
      return if unrendered.empty?

      raise MissingVariableError, "Missing variables: #{unrendered.join(', ')}"
    end
  end
end
