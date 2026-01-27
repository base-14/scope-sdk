# frozen_string_literal: true

if ENV['COVERAGE']
  require 'simplecov'
  SimpleCov.start do
    add_filter '/spec/'
    minimum_coverage 80
  end
end

require 'scope_client'
require 'webmock/rspec'

# Disable all real network connections - tests must use stubs
WebMock.disable_net_connect!

RSpec.configure do |config|
  config.expect_with :rspec do |expectations|
    expectations.include_chain_clauses_in_custom_matcher_descriptions = true
  end

  config.mock_with :rspec do |mocks|
    mocks.verify_partial_doubles = true
  end

  config.shared_context_metadata_behavior = :apply_to_host_groups
  config.filter_run_when_matching :focus
  config.example_status_persistence_file_path = '.rspec_status'
  config.disable_monkey_patching!
  config.order = :random
  Kernel.srand config.seed

  config.before do
    ScopeClient.reset_configuration!
    ScopeClient.configure do |c|
      c.org_id = 'test_org'
      c.api_key = 'test_api_key_12345'
      c.api_secret = 'test_api_secret'
      c.base_url = 'https://api.scope.io'
      c.auth_api_url = 'https://auth.scope.io'
    end

    # Stub auth API token endpoint
    stub_request(:post, 'https://auth.scope.io/v1/auth/sdk-token')
      .to_return(
        status: 200,
        body: {
          access_token: 'test_jwt_token',
          expires_in: 3600,
          token_type: 'Bearer'
        }.to_json,
        headers: { 'Content-Type' => 'application/json' }
      )
  end
end

Dir["#{__dir__}/support/**/*.rb"].sort.each { |f| require f }
