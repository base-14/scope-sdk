# Changelog

All notable changes to the Scope Client Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-01

### Added

- Initial release of the Scope Client Python SDK
- `ScopeClient` class for API interaction
- Prompt management methods:
  - `get_prompt()` - Fetch a prompt by ID
  - `get_prompt_latest()` - Fetch the latest version of a prompt
  - `get_prompt_production()` - Fetch the production version of a prompt
  - `get_prompt_version()` - Fetch a specific version
  - `list_prompts()` - List all prompts with pagination
  - `render_prompt()` - Fetch and render a prompt in one call
- Resource classes:
  - `Prompt` - Prompt resource with version fetching methods
  - `PromptVersion` - Version resource with rendering support
- Configuration system:
  - Environment variable support (`SCOPE_API_KEY`, `SCOPE_API_URL`, `SCOPE_ENVIRONMENT`)
  - Global configuration via `configure()`
  - Per-client configuration overrides
- Thread-safe TTL-based caching:
  - Configurable TTL
  - Per-request cache control
  - `clear_cache()` method
- Comprehensive error hierarchy:
  - `ScopeError` base class
  - API errors: `AuthenticationError`, `AuthorizationError`, `NotFoundError`, etc.
  - Resource errors: `ValidationError`, `MissingVariableError`, `NoProductionVersionError`
  - Connection errors: `ConnectionError`, `TimeoutError`
- Template rendering with `{{variable}}` syntax
- Automatic retry with exponential backoff
- Telemetry hooks for request/response logging
- Context manager support for automatic cleanup
- Type hints for all public APIs
- Comprehensive test suite with pytest

### Dependencies

- `httpx>=0.24.0,<1.0.0` - HTTP client

[Unreleased]: https://github.com/scope-io/scope-sdk/compare/python-v0.1.0...HEAD
[0.1.0]: https://github.com/scope-io/scope-sdk/releases/tag/python-v0.1.0
