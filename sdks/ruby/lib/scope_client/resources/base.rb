# frozen_string_literal: true

module ScopeClient
  module Resources
    class Base
      attr_reader :raw_data, :client

      def initialize(data, client: nil)
        @raw_data = data.freeze
        @client = client
        define_accessors
      end

      def [](key)
        @raw_data[key.to_s]
      end

      def to_h
        @raw_data
      end

      def to_json(*args)
        @raw_data.to_json(*args)
      end

      private

      def define_accessors
        @raw_data.each_key do |key|
          define_singleton_method(key) { @raw_data[key] }
          define_singleton_method(:"#{key}?") { !!@raw_data[key] } if boolean_like?(key)
        end
      end

      def boolean_like?(key)
        key.to_s.start_with?('has_', 'is_') || key.to_s.end_with?('_enabled')
      end
    end
  end
end
