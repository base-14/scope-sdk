# frozen_string_literal: true

require_relative "lib/scope_client/version"

Gem::Specification.new do |spec|
  spec.name          = "scope-client"
  spec.version       = ScopeClient::VERSION
  spec.authors       = ["Base14"]
  spec.email         = ["support@base14.io"]

  spec.summary       = "Ruby SDK for Scope Prompt Management Platform"
  spec.description   = "Read-only Ruby client for managing and rendering prompts from the Scope platform"
  spec.homepage      = "https://github.com/base14/scope-sdk"
  spec.license       = "BSD-3-Clause"

  spec.required_ruby_version = ">= 2.7.0"

  spec.metadata["homepage_uri"]          = spec.homepage
  spec.metadata["source_code_uri"]       = "https://github.com/base14/scope-sdk/tree/main/sdks/ruby"
  spec.metadata["changelog_uri"]         = "https://github.com/base14/scope-sdk/blob/main/sdks/ruby/CHANGELOG.md"
  spec.metadata["documentation_uri"]     = "https://docs.scope.io/sdk/ruby"
  spec.metadata["rubygems_mfa_required"] = "true"

  spec.files = Dir[
    "lib/**/*",
    "LICENSE",
    "README.md",
    "CHANGELOG.md"
  ]
  spec.require_paths = ["lib"]

  spec.add_dependency "faraday", ">= 2.0", "< 3.0"
  spec.add_dependency "faraday-retry", "~> 2.0"
end
