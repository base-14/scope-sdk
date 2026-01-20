#!/usr/bin/env ruby
# frozen_string_literal: true

# Error handling example for the Scope Client Ruby SDK
#
# Before running, set your API key:
#   export SCOPE_API_KEY=your_api_key
#
# Run with:
#   ruby examples/error_handling.rb

require_relative '../lib/scope_client'

ScopeClient.configure do |config|
  config.api_key = ENV.fetch('SCOPE_API_KEY', nil)
end

client = ScopeClient.client

puts '=== Scope Client Ruby SDK - Error Handling ==='
puts

# Example 1: Handling not found errors
puts '1. Handling NotFoundError...'
begin
  client.get_prompt('non-existent-prompt-id')
rescue ScopeClient::NotFoundError => e
  puts "   Caught NotFoundError: #{e.message}"
  puts "   HTTP Status: #{e.http_status}"
end
puts

# Example 2: Handling no production version
puts '2. Handling NoProductionVersionError...'
begin
  # This will raise NoProductionVersionError if no production version exists
  client.get_prompt_production('draft-only-prompt')
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

# Example 5: Handling authentication errors
puts '5. Handling AuthenticationError...'
begin
  # Create client with invalid API key
  bad_client = ScopeClient::Client.new(api_key: 'invalid_key')
  bad_client.get_prompt('some-prompt')
rescue ScopeClient::AuthenticationError => e
  puts "   Caught AuthenticationError: #{e.message}"
  puts "   HTTP Status: #{e.http_status}"
rescue ScopeClient::ApiError => e
  puts "   Caught ApiError: #{e.message}"
end
puts

# Example 6: Generic error handling pattern
puts '6. Recommended error handling pattern...'

def fetch_and_render_prompt(client, prompt_id, variables)
  prompt = client.get_prompt_production(prompt_id)
  prompt.render(variables)
rescue ScopeClient::NoProductionVersionError
  # Fallback to latest version if no production version
  prompt = client.get_prompt_latest(prompt_id)
  prompt.render(variables)
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
