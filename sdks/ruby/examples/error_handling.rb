#!/usr/bin/env ruby
# frozen_string_literal: true

# Error handling example for the Scope Client Ruby SDK
#
# Before running, set your environment variables:
#   export SCOPE_ORG_ID=your_org_id
#   export SCOPE_API_KEY=your_api_key
#   export SCOPE_API_SECRET=your_api_secret
#   export SCOPE_API_URL=https://api.scope.io
#   export SCOPE_AUTH_API_URL=https://auth.scope.io
#
# Run with:
#   ruby examples/error_handling.rb

require_relative '../lib/scope_client'

# Configure the client using credentials from environment
begin
  credentials = ScopeClient::Credentials::ApiKey.from_env
  ScopeClient.configure do |config|
    config.credentials = credentials
  end
rescue ScopeClient::ConfigurationError => e
  puts "Configuration error: #{e.message}"
  puts 'Please set SCOPE_ORG_ID, SCOPE_API_KEY, SCOPE_API_SECRET, SCOPE_API_URL, and SCOPE_AUTH_API_URL'
  exit 1
end

client = ScopeClient.client

puts '=== Scope Client Ruby SDK - Error Handling ==='
puts

# Example 1: Handling not found errors
puts '1. Handling NotFoundError...'
begin
  client.get_prompt_version('non-existent-prompt-id')
rescue ScopeClient::NoProductionVersionError => e
  puts "   Caught NoProductionVersionError: #{e.message}"
rescue ScopeClient::NotFoundError => e
  puts "   Caught NotFoundError: #{e.message}"
  puts "   HTTP Status: #{e.http_status}"
end
puts

# Example 2: Handling no production version
puts '2. Handling NoProductionVersionError...'
begin
  # This will raise NoProductionVersionError if no production version exists
  client.get_prompt_version('draft-only-prompt')
rescue ScopeClient::NoProductionVersionError => e
  puts "   Caught NoProductionVersionError: #{e.message}"
rescue ScopeClient::NotFoundError => e
  puts "   Caught NotFoundError: #{e.message}"
end
puts

# Example 3: Handling missing variables
puts '3. Handling MissingVariableError...'
begin
  # Simulate a prompt with variables
  version = ScopeClient::Resources::PromptVersion.new(
    'prompt_id' => 'test',
    'version_id' => 'v1',
    'content' => 'Hello {{name}}, your order {{order_id}} is ready!',
    'variables' => %w[name order_id],
    'status' => 'published'
  )

  # This will raise MissingVariableError because order_id is missing
  version.render({ name: 'Alice' })
rescue ScopeClient::MissingVariableError => e
  puts "   Caught MissingVariableError: #{e.message}"
end
puts

# Example 4: Handling validation errors
puts '4. Handling ValidationError...'
begin
  version = ScopeClient::Resources::PromptVersion.new(
    'prompt_id' => 'test',
    'version_id' => 'v1',
    'content' => 'Hello {{name}}!',
    'variables' => ['name'],
    'status' => 'published'
  )

  # This will raise ValidationError because 'unknown' is not a declared variable
  version.render({ name: 'Alice', unknown: 'value' })
rescue ScopeClient::ValidationError => e
  puts "   Caught ValidationError: #{e.message}"
end
puts

# Example 5: Generic error handling pattern
puts '5. Recommended error handling pattern...'

def fetch_and_render_prompt(client, prompt_id, variables)
  version = client.get_prompt_version(prompt_id)
  version.render(variables)
rescue ScopeClient::NoProductionVersionError
  # Fallback to latest version if no production version
  version = client.get_prompt_version(prompt_id, label: :latest)
  version.render(variables)
rescue ScopeClient::NotFoundError
  puts "   Prompt not found: #{prompt_id}"
  nil
rescue ScopeClient::MissingVariableError => e
  puts "   Missing required variables: #{e.message}"
  nil
rescue ScopeClient::AuthenticationError
  puts '   Authentication failed - check your API key'
  nil
rescue ScopeClient::RateLimitError
  puts '   Rate limit exceeded - please retry later'
  nil
rescue ScopeClient::ApiError => e
  puts "   API error: #{e.message} (HTTP #{e.http_status})"
  nil
end

result = fetch_and_render_prompt(client, 'customer-greeting', { name: 'Alice' })
if result
  puts "   Rendered: #{result}"
else
  puts '   Failed to render prompt'
end
puts

puts '=== Done ==='
