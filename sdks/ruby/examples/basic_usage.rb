#!/usr/bin/env ruby
# frozen_string_literal: true

# Basic usage example for the Scope Client Ruby SDK
#
# Before running, set your environment variables:
#   export SCOPE_ORG_ID=your_org_id
#   export SCOPE_API_KEY=your_api_key
#   export SCOPE_API_SECRET=your_api_secret
#   export SCOPE_API_URL=https://api.scope.io
#   export SCOPE_AUTH_API_URL=https://auth.scope.io
#
# Run with:
#   ruby examples/basic_usage.rb

require_relative '../lib/scope_client'

# Configure the client using credentials from environment
begin
  credentials = ScopeClient::Credentials::ApiKey.from_env
rescue ScopeClient::ConfigurationError => e
  puts "Configuration error: #{e.message}"
  puts 'Please set SCOPE_ORG_ID, SCOPE_API_KEY, SCOPE_API_SECRET, SCOPE_API_URL, and SCOPE_AUTH_API_URL'
  exit 1
end

ScopeClient.configure do |config|
  config.credentials = credentials
  config.cache_ttl = 300 # Cache prompts for 5 minutes
end

# Create a client instance
client = ScopeClient.client

puts '=== Scope Client Ruby SDK - Basic Usage ==='
puts

# Example 1: Get production version
puts '1. Getting production version...'
begin
  version = client.get_prompt_version('customer-greeting')
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

# Example 2: Render a prompt with variables
puts '2. Rendering a prompt...'
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
rescue ScopeClient::NoProductionVersionError
  puts '   No production version exists'
end
puts

# Example 3: Working with caching
puts '3. Caching demonstration...'
begin
  # First request - fetches from API
  start_time = Time.now
  client.get_prompt_version('customer-greeting')
  first_duration = Time.now - start_time
  puts "   First request: #{(first_duration * 1000).round(2)}ms"

  # Second request - served from cache
  start_time = Time.now
  client.get_prompt_version('customer-greeting')
  second_duration = Time.now - start_time
  puts "   Second request (cached): #{(second_duration * 1000).round(2)}ms"

  # Bypass cache
  start_time = Time.now
  client.get_prompt_version('customer-greeting', cache: false)
  third_duration = Time.now - start_time
  puts "   Third request (cache bypassed): #{(third_duration * 1000).round(2)}ms"
rescue ScopeClient::NotFoundError, ScopeClient::NoProductionVersionError
  puts '   Prompt not found or no production version'
end
puts

puts '=== Done ==='
