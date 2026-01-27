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

### Ruby

```ruby
gem install scope-client
```

```ruby
require 'scope_client'

# Configure with credentials
ScopeClient.configure do |config|
  config.org_id = ENV['SCOPE_ORG_ID']
  config.api_key = ENV['SCOPE_API_KEY']
  config.api_secret = ENV['SCOPE_API_SECRET']
end

# Fetch and render a prompt
client = ScopeClient.client
rendered = client.render_prompt('my-prompt', {
  customer_name: 'Alice',
  product: 'Widget'
})
```

### Python

```bash
pip install scope-client
```

```python
import scope_client

# Configure with credentials
scope_client.configure(
    org_id="my-org",
    api_key="key_abc123",
    api_secret="secret_xyz"
)

# Fetch and render a prompt
client = scope_client.client()
rendered = client.render_prompt('my-prompt', {
    'customer_name': 'Alice',
    'product': 'Widget'
})
```

## Authentication

All SDKs use JWT-based authentication. Credentials are exchanged for a JWT token which is automatically managed and refreshed by the SDK.

Authentication requires three credentials:

1. **Organization ID** (`SCOPE_ORG_ID`): Your organization identifier
2. **API Key** (`SCOPE_API_KEY`): Your API key ID
3. **API Secret** (`SCOPE_API_SECRET`): Your API key secret

These can be set via environment variables (recommended) or passed directly during configuration.

Generate API keys from the Scope UI under Settings > Applications.

## Documentation

- [Ruby SDK Documentation](./sdks/ruby/README.md)
- [Python SDK Documentation](./sdks/python/README.md)
- [API Reference](https://docs.base14.io/scope)

## License

BSD-3-Clause. See [LICENSE](./LICENSE).
