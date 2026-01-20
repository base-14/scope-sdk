#!/usr/bin/env ruby
# frozen_string_literal: true

# Basic usage example for the Scope Client Ruby SDK
#
# Before running, set your API key:
#   export SCOPE_API_KEY=your_api_key
#
# Run with:
#   ruby examples/basic_usage.rb

require_relative '../lib/scope_client'

# Configure the client (optional if using SCOPE_API_KEY env var)
ScopeClient.configure do |config|
  config.api_key = ENV.fetch('SCOPE_API_KEY', nil)
  config.cache_ttl = 300 # Cache prompts for 5 minutes
end

# Create a client instance
client = ScopeClient.client

puts '=== Scope Client Ruby SDK - Basic Usage ==='
puts

# Example 1: Get prompt metadata
puts '1. Getting prompt metadata...'
begin
  prompt = client.get_prompt('customer-greeting')
  puts "   Name: #{prompt.name}"
  puts "   Latest version: #{prompt.latest_version}"
  puts "   Production version: #{prompt.production_version}"
  puts "   Tags: #{prompt.tags.join(', ')}"
rescue ScopeClient::NotFoundError
  puts "   Prompt not found (this is expected if 'customer-greeting' doesn't exist)"
end
puts

# Example 2: Get production version
puts '2. Getting production version...'
begin
  version = client.get_prompt_production('customer-greeting')
  puts "   Version: v#{version.version}"
  puts "   Status: #{version.status}"
  puts "   Variables: #{version.variables.join(', ')}"
  puts "   Content preview: #{version.content[0..100]}..."
rescue ScopeClient::NoProductionVersionError
  puts '   No production version exists'
rescue ScopeClient::NotFoundError
  puts '   Prompt not found'
end
puts

# Example 3: Render a prompt with variables
puts '3. Rendering a prompt...'
begin
  rendered = client.render_prompt('customer-greeting', {
                                    customer_name: 'Alice',
                                    company_name: 'Acme Corp',
                                    product: 'Widget Pro'
                                  })
  puts '   Rendered content:'
  puts "   #{rendered}"
rescue ScopeClient::MissingVariableError => e
  puts "   Missing variables: #{e.message}"
rescue ScopeClient::NotFoundError
  puts '   Prompt not found'
end
puts

# Example 4: List prompts with filters
puts '4. Listing prompts...'
begin
  result = client.list_prompts(
    limit: 5,
    status: 'has_production_version',
    sort_by: 'updated_at',
    sort_direction: 'desc'
  )
  puts "   Found #{result[:data].length} prompts:"
  result[:data].each do |p|
    puts "   - #{p.name} (#{p.production_version || 'no production version'})"
  end
  puts "   Has more: #{result[:meta]['has_more']}"
rescue ScopeClient::ApiError => e
  puts "   API error: #{e.message}"
end
puts

# Example 5: Working with caching
puts '5. Caching demonstration...'
begin
  # First request - fetches from API
  start_time = Time.now
  client.get_prompt_latest('customer-greeting')
  first_duration = Time.now - start_time
  puts "   First request: #{(first_duration * 1000).round(2)}ms"

  # Second request - served from cache
  start_time = Time.now
  client.get_prompt_latest('customer-greeting')
  second_duration = Time.now - start_time
  puts "   Second request (cached): #{(second_duration * 1000).round(2)}ms"

  # Bypass cache
  start_time = Time.now
  client.get_prompt_latest('customer-greeting', cache: false)
  third_duration = Time.now - start_time
  puts "   Third request (cache bypassed): #{(third_duration * 1000).round(2)}ms"
rescue ScopeClient::NotFoundError
  puts '   Prompt not found'
end
puts

puts '=== Done ==='
