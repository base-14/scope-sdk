# Scope SDK

Official SDK clients for the [Scope Platform](https://scope.play.base14.io/).

## Available SDKs

| Language | Package | Status |
|----------|---------|--------|
| Ruby | [scope-client](./sdks/ruby) | Available |
| Python | [scope-client](./sdks/python) | Available |
| Node.js | @scope/client | Coming Soon |
| Java/JVM | io.scope:scope-client | Coming Soon |

## Overview

Scope SDKs provide read-only access to the Scope Platform, enabling you to:

- Fetch production and draft prompts
- Render prompts with variable substitution
- Cache prompts for performance
- Integrate with your LLM workflows

## Quick Start

### Python

Install from git (not yet published to PyPI):

```bash
pip install git+https://github.com/base14/scope-sdk.git#subdirectory=sdks/python
```

```python
from scope_client import ScopeClient, ApiKeyCredentials

# Create credentials from environment variables
credentials = ApiKeyCredentials.from_env()
# Or explicitly:
# credentials = ApiKeyCredentials(
#     org_id="my-org",
#     api_key="key_abc123",
#     api_secret="secret_xyz"
# )

# Create a client
client = ScopeClient(credentials=credentials)

# Fetch and render a prompt
rendered = client.render_prompt('my-prompt', {
    'customer_name': 'Alice',
    'product': 'Widget'
})
```

### Ruby

Add to your Gemfile (not yet published to RubyGems):

```ruby
gem 'scope-client', git: 'https://github.com/base14/scope-sdk.git', glob: 'sdks/ruby/*.gemspec'
```

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

# Fetch and render a prompt
client = ScopeClient.client
rendered = client.render_prompt('my-prompt', {
  customer_name: 'Alice',
  product: 'Widget'
})
```

## Authentication

All SDKs use JWT-based authentication with an extensible credentials system. The primary authentication method uses API key credentials.

### Credentials

Authentication requires three values:

1. **Organization ID** (`SCOPE_ORG_ID`): Your organization identifier
2. **API Key** (`SCOPE_API_KEY`): Your API key ID
3. **API Secret** (`SCOPE_API_SECRET`): Your API key secret

These can be loaded from environment variables using `ApiKeyCredentials.from_env()` (Python) or `Credentials::ApiKey.from_env` (Ruby), or passed directly when creating credentials.

Generate API keys from the Scope UI under Settings > Applications.

### Environment Variables

```bash
export SCOPE_ORG_ID="my-org"
export SCOPE_API_KEY="key_abc123"
export SCOPE_API_SECRET="secret_xyz"
```

## Documentation

- [Ruby SDK Documentation](./sdks/ruby/README.md)
- [Python SDK Documentation](./sdks/python/README.md)
- [API Reference](https://docs.base14.io/scope)

## License

BSD-3-Clause. See [LICENSE](./LICENSE).
