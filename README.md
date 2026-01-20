# Scope SDK

Official SDK clients for the [Scope Prompt Management Platform](https://scope.io).

## Available SDKs

| Language | Package | Status |
|----------|---------|--------|
| Ruby | [scope-client](./sdks/ruby) | Available |
| Python | [scope-client](./sdks/python) | Available |
| Node.js | @scope/client | Coming Soon |
| Java/JVM | io.scope:scope-client | Coming Soon |

## Overview

Scope SDKs provide read-only access to the Scope Prompt Management Platform, enabling you to:

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

# Configure with API key
ScopeClient.configure do |config|
  config.api_key = ENV['SCOPE_API_KEY']
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

# Configure with API key
scope_client.configure(api_key="sk_your_api_key")

# Fetch and render a prompt
client = scope_client.client()
rendered = client.render_prompt('my-prompt', {
    'customer_name': 'Alice',
    'product': 'Widget'
})
```

## Authentication

All SDKs support authentication via:

1. **Environment variable** (recommended): Set `SCOPE_API_KEY`
2. **Direct configuration**: Pass API key during client initialization

Generate API keys from the Scope UI under Settings > Applications.

## Documentation

- [Ruby SDK Documentation](./sdks/ruby/README.md)
- [Python SDK Documentation](./sdks/python/README.md)
- [API Reference](https://docs.scope.io/api)

## License

BSD-3-Clause. See [LICENSE](./LICENSE).
