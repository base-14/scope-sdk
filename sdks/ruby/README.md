# Scope Client Ruby SDK

Official Ruby SDK for the [Scope Platform](https://scope.play.base14.io/).

[![CI](https://github.com/base14/scope-sdk/actions/workflows/scope-ruby-sdk-ci.yml/badge.svg)](https://github.com/base14/scope-sdk/actions)

## Installation

> **Note:** This gem is not yet published to RubyGems. Install from the git repository.

Add to your Gemfile:

```ruby
gem 'scope-client', git: 'https://github.com/base14/scope-sdk.git', glob: 'sdks/ruby/*.gemspec'
```

Then run:

```bash
bundle install
```

## Quick Start

```ruby
require 'scope_client'

# Create credentials from environment variables
credentials = ScopeClient::Credentials::ApiKey.from_env
# Or explicitly:
# credentials = ScopeClient::Credentials::ApiKey.new(
#   org_id: 'my-org',
#   api_key: 'key_abc123',
#   api_secret: 'secret_xyz'
# )

# Configure globally
ScopeClient.configure do |config|
  config.credentials = credentials
end

# Create a client
client = ScopeClient.client

# Get and render a production prompt by name (or use prompt ID like "prompt_01HXYZ...")
rendered = client.render_prompt('my-greeting-prompt', {
  user_name: 'Alice',
  product: 'Widget'
})

puts rendered
```

## Configuration

### Environment Variables

The SDK can load credentials from environment variables via `Credentials::ApiKey.from_env`:

- `SCOPE_ORG_ID` - Your organization identifier (required)
- `SCOPE_API_KEY` - Your API key ID (required)
- `SCOPE_API_SECRET` - Your API key secret (required)
- `SCOPE_API_URL` - API base URL (required)
- `SCOPE_AUTH_API_URL` - Auth API URL for token exchange (required)
- `SCOPE_ENVIRONMENT` - Environment name (optional)
- `SCOPE_TOKEN_REFRESH_BUFFER` - Seconds before token expiry to refresh (optional)

### Client Options

```ruby
# Create credentials
credentials = ScopeClient::Credentials::ApiKey.new(
  org_id: 'my-org',
  api_key: 'key_abc123',
  api_secret: 'secret_xyz'
)

# Pass credentials via options
client = ScopeClient.client(
  credentials: credentials,
  timeout: 60,                  # Request timeout (seconds)
  cache_enabled: true,          # Enable response caching
  cache_ttl: 300,              # Cache TTL (seconds)
  max_retries: 3               # Max retry attempts
)
```

### Global Configuration

```ruby
credentials = ScopeClient::Credentials::ApiKey.from_env

ScopeClient.configure do |config|
  config.credentials = credentials
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

All prompt methods accept either a prompt ID (e.g., `prompt_01HXYZ...`) or a prompt name. The API auto-detects: if the value starts with `prompt_` and is a valid ULID, it's treated as an ID; otherwise, it's treated as a name.

```ruby
# Get production version by name (recommended for production use)
prompt = client.get_prompt_production('my-greeting-prompt')

# Or by ID
prompt = client.get_prompt_production('prompt_01HXYZ...')

# Get latest version (may be draft)
prompt = client.get_prompt_latest('my-greeting-prompt')

# Get specific version
prompt = client.get_prompt_version('my-greeting-prompt', 'version-id')

# Get prompt metadata
prompt = client.get_prompt('my-greeting-prompt')

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
# Render with production version using prompt name (default)
text = client.render_prompt('greeting-template', { name: 'Alice' })

# Render with latest version
text = client.render_prompt('greeting-template', { name: 'Alice' }, version: :latest)

# Render specific version
text = client.render_prompt('greeting-template', { name: 'Alice' }, version: 'ver-123')

# Or render from a prompt object (using name or ID)
prompt = client.get_prompt_production('greeting-template')
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

# Create credentials from environment
credentials = ScopeClient::Credentials::ApiKey.from_env
ScopeClient.configure { |c| c.credentials = credentials }

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

# Create credentials from environment
credentials = ScopeClient::Credentials::ApiKey.from_env
ScopeClient.configure { |c| c.credentials = credentials }

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
