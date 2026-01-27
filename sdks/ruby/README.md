# Scope Client Ruby SDK

Official Ruby SDK for the [Scope Platform](https://scope.play.base14.io/).

[![Gem Version](https://badge.fury.io/rb/scope-client.svg)](https://rubygems.org/gems/scope-client)
[![CI](https://github.com/base14/scope-sdk/actions/workflows/scope-ruby-sdk-ci.yml/badge.svg)](https://github.com/base14/scope-sdk/actions)

## Installation

Add to your Gemfile:

```ruby
gem 'scope-client'
```

Or install directly:

```bash
gem install scope-client
```

## Quick Start

```ruby
require 'scope_client'

# Configure globally (or use environment variables)
ScopeClient.configure do |config|
  config.org_id = 'my-org'
  config.api_key = 'key_abc123'
  config.api_secret = 'secret_xyz'
end

# Create a client
client = ScopeClient.client

# Get and render a production prompt
rendered = client.render_prompt('my-prompt-id', {
  user_name: 'Alice',
  product: 'Widget'
})

puts rendered
```

## Configuration

### Environment Variables

- `SCOPE_ORG_ID` - Your organization identifier (required)
- `SCOPE_API_KEY` - Your API key ID (required)
- `SCOPE_API_SECRET` - Your API key secret (required)
- `SCOPE_API_URL` - Custom API base URL (optional)
- `SCOPE_AUTH_API_URL` - Auth API URL for token exchange (optional)
- `SCOPE_ENVIRONMENT` - Environment name (optional)
- `SCOPE_TOKEN_REFRESH_BUFFER` - Seconds before token expiry to refresh (optional)

### Client Options

```ruby
client = ScopeClient.client(
  org_id: 'my-org',            # Organization identifier
  api_key: 'key_abc123',       # API key ID
  api_secret: 'secret_xyz',    # API key secret
  timeout: 60,                  # Request timeout (seconds)
  cache_enabled: true,          # Enable response caching
  cache_ttl: 300,              # Cache TTL (seconds)
  max_retries: 3               # Max retry attempts
)
```

### Global Configuration

```ruby
ScopeClient.configure do |config|
  config.org_id = 'my-org'
  config.api_key = 'key_abc123'
  config.api_secret = 'secret_xyz'
  config.base_url = 'https://api.scope.io'
  config.auth_api_url = 'https://auth.scope.io'
  config.timeout = 30
  config.cache_enabled = true
  config.cache_ttl = 300
  config.max_retries = 3
  config.telemetry_enabled = true
  config.token_refresh_buffer = 60
end
```

## API Reference

### Fetching Prompts

```ruby
# Get production version (recommended for production use)
prompt = client.get_prompt_production('prompt-id')

# Get latest version (may be draft)
prompt = client.get_prompt_latest('prompt-id')

# Get specific version
prompt = client.get_prompt_version('prompt-id', 'version-id')

# Get prompt metadata
prompt = client.get_prompt('prompt-id')

# List prompts with filters
results = client.list_prompts(
  search: 'onboarding',
  tags: 'email,marketing',
  status: 'has_production_version',
  limit: 20
)
```

### Rendering Prompts

```ruby
# Render with production version (default)
text = client.render_prompt('prompt-id', { name: 'Alice' })

# Render with latest version
text = client.render_prompt('prompt-id', { name: 'Alice' }, version: :latest)

# Render specific version
text = client.render_prompt('prompt-id', { name: 'Alice' }, version: 'ver-123')

# Or render from a prompt object
prompt = client.get_prompt_production('prompt-id')
text = prompt.render({ name: 'Alice' })
```

### Working with Prompt Versions

```ruby
prompt = client.get_prompt_production('prompt-id')

# Access version properties
puts prompt.content          # Raw template content
puts prompt.variables        # Array of variable names
puts prompt.version          # Version number
puts prompt.status           # draft, published, or archived

# Check status
prompt.draft?                # true if draft
prompt.published?            # true if published
prompt.production?           # alias for published?
prompt.archived?             # true if archived
```

## Error Handling

```ruby
begin
  prompt = client.get_prompt_production('prompt-id')
rescue ScopeClient::InvalidCredentialsError
  # Invalid org_id, api_key, or api_secret
rescue ScopeClient::TokenRefreshError
  # Failed to refresh JWT token
rescue ScopeClient::AuthenticationError
  # Authentication failed
rescue ScopeClient::AuthorizationError
  # Insufficient permissions
rescue ScopeClient::NotFoundError
  # Prompt not found
rescue ScopeClient::NoProductionVersionError
  # No production version exists
rescue ScopeClient::MissingVariableError => e
  # Missing required variables
  puts "Missing: #{e.message}"
rescue ScopeClient::RateLimitError
  # Rate limit exceeded
rescue ScopeClient::ServerError
  # Server error (5xx)
rescue ScopeClient::ApiError => e
  # Other API errors
  puts "Error: #{e.message} (HTTP #{e.http_status})"
end
```

## Caching

Caching is enabled by default with a 5-minute TTL.

```ruby
# Disable cache for a specific request
prompt = client.get_prompt_production('prompt-id', cache: false)

# Use custom TTL for a request
prompt = client.get_prompt_production('prompt-id', cache_ttl: 60)

# Clear all cached data
client.clear_cache

# Disable caching globally
ScopeClient.configure do |config|
  config.cache_enabled = false
end
```

## Telemetry Hooks

```ruby
ScopeClient::Middleware::Telemetry.on_request = ->(data) {
  puts "Request: #{data[:method]} #{data[:url]}"
}

ScopeClient::Middleware::Telemetry.on_response = ->(data) {
  puts "Response: #{data[:status]} in #{data[:duration]}s"
}

ScopeClient::Middleware::Telemetry.on_error = ->(data) {
  puts "Error: #{data[:error].message}"
}
```

## Integration Examples

### OpenAI

```ruby
require 'scope_client'
require 'openai'

# Credentials loaded from SCOPE_ORG_ID, SCOPE_API_KEY, SCOPE_API_SECRET env vars
scope = ScopeClient.client
openai = OpenAI::Client.new

# Get and render prompt
prompt = scope.get_prompt_production('customer-support')
rendered = prompt.render({
  customer_name: 'Alice',
  issue: 'billing question'
})

# Use with OpenAI
response = openai.chat(
  parameters: {
    model: 'gpt-4',
    messages: [{ role: 'user', content: rendered }]
  }
)
```

### Anthropic Claude

```ruby
require 'scope_client'
require 'anthropic'

# Credentials loaded from SCOPE_ORG_ID, SCOPE_API_KEY, SCOPE_API_SECRET env vars
scope = ScopeClient.client
anthropic = Anthropic::Client.new

rendered = scope.render_prompt('assistant-prompt', {
  context: 'Technical support',
  user_query: params[:query]
})

response = anthropic.messages(
  model: 'claude-3-opus-20240229',
  max_tokens: 1024,
  messages: [{ role: 'user', content: rendered }]
)
```

## Requirements

- Ruby 2.7+
- Faraday 2.x

## Development

```bash
# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-coverage

# Run linter
make lint

# Auto-fix lint issues
make lint-fix

# Build gem
make build

# Generate documentation
make docs

# Interactive console
make console
```

## License

BSD-3-Clause. See [LICENSE](../../LICENSE).
