# Scope Client Python SDK

Official Python SDK for the [Scope Platform](https://scope.play.base14.io/).

## Installation

> **Note:** This package is not yet published to PyPI. Install from the git repository.

```bash
pip install git+https://github.com/base14/scope-sdk.git#subdirectory=sdks/python
```

## Requirements

- Python 3.9+

## Quick Start

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

# Fetch and render a prompt by name (or use prompt ID like "prompt_01HXYZ...")
version = client.get_prompt_production("greeting-template")
rendered = version.render({"name": "Alice"})
print(rendered)  # "Hello, Alice!"
```

## Configuration

### Environment Variables

The SDK can load credentials from environment variables via `ApiKeyCredentials.from_env()`:

```bash
export SCOPE_ORG_ID="my-org"
export SCOPE_API_KEY="key_abc123"
export SCOPE_API_SECRET="secret_xyz"
export SCOPE_API_URL="https://api.scope.io"       # Optional
export SCOPE_AUTH_API_URL="https://auth.scope.io" # Optional
export SCOPE_ENVIRONMENT="production"              # Optional
export SCOPE_TOKEN_REFRESH_BUFFER="60"             # Optional
```

### Programmatic Configuration

```python
from scope_client import ScopeClient, ApiKeyCredentials, Configuration

# Create credentials
credentials = ApiKeyCredentials(
    org_id="my-org",
    api_key="key_abc123",
    api_secret="secret_xyz"
)

# Option 1: Pass credentials directly to client
client = ScopeClient(credentials=credentials)

# Option 2: Use Configuration object
config = Configuration(
    credentials=credentials,
    base_url="https://api.scope.io",
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    timeout=30,
    max_retries=3,
)
client = ScopeClient(config=config)

# Option 3: Global configuration
import scope_client

scope_client.configure(
    credentials=ApiKeyCredentials.from_env(),
    cache_enabled=True,
    cache_ttl=600
)
client = scope_client.client()
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `credentials` | Credentials | None | Credentials instance for authentication (required) |
| `base_url` | str | `https://api.scope.io` | API base URL |
| `auth_api_url` | str | `https://auth.scope.io` | Auth API URL for token exchange |
| `api_version` | str | `v1` | API version |
| `timeout` | int | 30 | Request timeout in seconds |
| `open_timeout` | int | 10 | Connection timeout in seconds |
| `cache_enabled` | bool | True | Enable response caching |
| `cache_ttl` | int | 300 | Cache TTL in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `retry_base_delay` | float | 0.5 | Base delay between retries |
| `retry_max_delay` | float | 30.0 | Maximum delay between retries |
| `telemetry_enabled` | bool | True | Enable telemetry hooks |
| `environment` | str | `production` | Environment name |
| `token_refresh_buffer` | int | 60 | Seconds before token expiry to refresh |

## Usage

### Fetching Prompts

All prompt methods accept either a prompt ID (e.g., `prompt_01HXYZ...`) or a prompt name. The API auto-detects: if the value starts with `prompt_` and is a valid ULID, it's treated as an ID; otherwise, it's treated as a name.

```python
from scope_client import ScopeClient, ApiKeyCredentials

credentials = ApiKeyCredentials.from_env()
client = ScopeClient(credentials=credentials)

# Get a prompt by name
prompt = client.get_prompt("my-greeting-prompt")
print(f"Prompt: {prompt.name}")
print(f"Has production: {prompt.has_production_version}")

# Or by ID
prompt = client.get_prompt("prompt_01HXYZ...")

# Get the production version by name
version = client.get_prompt_production("my-greeting-prompt")
print(f"Content: {version.content}")
print(f"Variables: {version.variables}")

# Get the latest version
latest = client.get_prompt_latest("my-greeting-prompt")

# Get a specific version
specific = client.get_prompt_version("my-greeting-prompt", "version-123")
```

### Rendering Prompts

```python
# Render via the version object (using prompt name)
version = client.get_prompt_production("greeting-template")
rendered = version.render({
    "name": "Alice",
    "time_of_day": "morning",
})
print(rendered)  # "Good morning, Alice!"

# Or render directly via the client (works with name or ID)
rendered = client.render_prompt(
    "greeting-template",  # prompt name
    {"name": "Bob", "time_of_day": "evening"},
    version="production",  # or "latest" or a specific version ID
)
```

### Listing Prompts

```python
result = client.list_prompts(page=1, per_page=20)

for prompt in result["data"]:
    print(f"- {prompt.name} ({prompt.id})")

print(f"Total: {result['meta']['total']}")
```

### Caching

Caching is enabled by default. You can control it per-request:

```python
# Bypass cache for this request
prompt = client.get_prompt("my-prompt", cache=False)

# Use custom TTL for this request
prompt = client.get_prompt("my-prompt", cache_ttl=60)

# Clear all cached data
client.clear_cache()
```

### Error Handling

```python
from scope_client import (
    ScopeError,
    AuthenticationError,
    InvalidCredentialsError,
    TokenRefreshError,
    NotFoundError,
    NoProductionVersionError,
    MissingVariableError,
    RateLimitError,
)

try:
    version = client.get_prompt_production("my-prompt")
    rendered = version.render({"name": "Alice"})
except InvalidCredentialsError:
    print("Invalid credentials (org_id, api_key, or api_secret)")
except TokenRefreshError:
    print("Failed to refresh JWT token")
except AuthenticationError:
    print("Authentication failed")
except NotFoundError:
    print("Prompt not found")
except NoProductionVersionError as e:
    print(f"No production version for: {e.prompt_id}")
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except ScopeError as e:
    print(f"API error: {e}")
```

### Telemetry

Register callbacks to observe requests and responses:

```python
from scope_client import Telemetry, RequestInfo, ResponseInfo, ErrorInfo

def log_request(info: RequestInfo):
    print(f"Request: {info.method} {info.url}")

def log_response(info: ResponseInfo):
    print(f"Response: {info.status_code} in {info.elapsed_ms:.2f}ms")

def log_error(info: ErrorInfo):
    print(f"Error: {info.error}")

Telemetry.on_request(log_request)
Telemetry.on_response(log_response)
Telemetry.on_error(log_error)
```

### Context Manager

The client can be used as a context manager for automatic cleanup:

```python
from scope_client import ScopeClient, ApiKeyCredentials

credentials = ApiKeyCredentials.from_env()
with ScopeClient(credentials=credentials) as client:
    prompt = client.get_prompt("my-prompt")
    # Connection is automatically closed when exiting the context
```

## Error Types

| Error | Description |
|-------|-------------|
| `ScopeError` | Base class for all SDK errors |
| `ConfigurationError` | Configuration problem |
| `MissingApiKeyError` | API key not provided |
| `ApiError` | Base class for API errors |
| `AuthenticationError` | Invalid API key (401) |
| `AuthorizationError` | Insufficient permissions (403) |
| `NotFoundError` | Resource not found (404) |
| `ConflictError` | Resource conflict (409) |
| `RateLimitError` | Rate limit exceeded (429) |
| `ServerError` | Server error (5xx) |
| `ConnectionError` | Network connection failure |
| `TimeoutError` | Request timeout |
| `TokenRefreshError` | JWT token refresh failed |
| `InvalidCredentialsError` | Invalid org_id, api_key, or api_secret |
| `ResourceError` | Base class for resource errors |
| `ValidationError` | Validation failure |
| `RenderError` | Template rendering failure |
| `MissingVariableError` | Missing template variable |
| `NoProductionVersionError` | No production version exists |

## Development

```bash
# Clone the repository
git clone https://github.com/scope-io/scope-sdk.git
cd scope-sdk/sdks/python

# Install development dependencies
make install

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

## License

BSD-3-Clause. See [LICENSE](../../LICENSE).
