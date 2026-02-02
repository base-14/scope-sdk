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

# Get and render a prompt (defaults to production version)
version = client.get_prompt_version('my-greeting-prompt')
rendered = version.render(user_name: 'Alice', product: 'Widget')

puts rendered

# Access prompt metadata
model = version.get_metadata('model')  # e.g., 'gpt-4'
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

### Fetching Prompt Versions

All prompt methods accept either a prompt ID (e.g., `prompt_01HXYZ...`) or a prompt name. The API auto-detects: if the value starts with `prompt_` and is a valid ULID, it's treated as an ID; otherwise, it's treated as a name.

```ruby
# Get a prompt version (defaults to production)
version = client.get_prompt_version('my-greeting-prompt')
puts version.content       # Template content
puts version.variables     # Array of variable names
puts version.type          # "text" or "chat"

# Get latest version
latest = client.get_prompt_version('my-greeting-prompt', label: :latest)

# Get production version explicitly
production = client.get_prompt_version('my-greeting-prompt', label: :production)

# Get specific version by ID
specific = client.get_prompt_version('my-greeting-prompt', version: 'version-123')
```

### Rendering Prompts

```ruby
# Render via the version object
version = client.get_prompt_version('greeting-template')
text = version.render(name: 'Alice', time_of_day: 'morning')
puts text  # "Good morning, Alice!"

# Or render directly via the client
text = client.render_prompt('greeting-template', { name: 'Alice' })

# Render with latest version
text = client.render_prompt('greeting-template', { name: 'Alice' }, label: :latest)
```

### Accessing Metadata

Prompt versions can include metadata (e.g., model configuration) set in the Scope UI:

```ruby
version = client.get_prompt_version('my-prompt')

# Access all metadata
puts version.metadata  # {"model" => "gpt-4", "temperature" => 0.7}

# Get specific metadata values
model = version.get_metadata('model')  # "gpt-4"
temperature = version.get_metadata('temperature', 0.7)  # with default
max_tokens = version.get_metadata('max_tokens')  # nil if not set

# Use metadata with your LLM client
response = openai.chat(
  parameters: {
    model: version.get_metadata('model', 'gpt-4'),
    temperature: version.get_metadata('temperature', 0.7),
    messages: [{ role: 'user', content: version.render(name: 'Alice') }]
  }
)
```

### Working with Prompt Versions

```ruby
version = client.get_prompt_version('prompt-id')

# Access version properties
puts version.content          # Raw template content
puts version.variables        # Array of variable names
puts version.version          # Version number
puts version.status           # draft, published, or archived
puts version.type             # text or chat

# Check status
version.draft?                # true if draft
version.published?            # true if published
version.production?           # alias for published?
version.archived?             # true if archived
```

## Error Handling

```ruby
begin
  version = client.get_prompt_version('prompt-id')
  rendered = version.render(name: 'Alice')
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
version = client.get_prompt_version('prompt-id', cache: false)

# Use custom TTL for a request
version = client.get_prompt_version('prompt-id', cache_ttl: 60)

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

# Get prompt version and render
version = scope.get_prompt_version('customer-support')
rendered = version.render(
  customer_name: 'Alice',
  issue: 'billing question'
)

# Use metadata for model configuration
response = openai.chat(
  parameters: {
    model: version.get_metadata('model', 'gpt-4'),
    temperature: version.get_metadata('temperature', 0.7),
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

version = scope.get_prompt_version('assistant-prompt')
rendered = version.render(
  context: 'Technical support',
  user_query: params[:query]
)

response = anthropic.messages(
  model: version.get_metadata('model', 'claude-3-opus-20240229'),
  max_tokens: version.get_metadata('max_tokens', 1024),
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
