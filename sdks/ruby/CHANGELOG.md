# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-20

### Added

- Initial release of the Scope Client Ruby SDK
- `ScopeClient.client` for creating client instances
- `ScopeClient.configure` for global configuration
- Client methods:
  - `get_prompt` - Get prompt metadata by ID
  - `get_prompt_latest` - Get latest version of a prompt
  - `get_prompt_production` - Get production version of a prompt
  - `get_prompt_version` - Get specific version of a prompt
  - `list_prompts` - List prompts with pagination and filters
  - `render_prompt` - Render prompt with variable substitution
  - `clear_cache` - Clear cached data
- Thread-safe caching with configurable TTL
- Automatic retries with exponential backoff
- Telemetry hooks for request/response monitoring
- Comprehensive error hierarchy:
  - `AuthenticationError` (401)
  - `AuthorizationError` (403)
  - `NotFoundError` (404)
  - `RateLimitError` (429)
  - `ServerError` (5xx)
  - `MissingVariableError` for template rendering
  - `NoProductionVersionError` when no production version exists
- Environment variable configuration (`SCOPE_API_KEY`, `SCOPE_API_URL`)
- Full YARD documentation
- RSpec test suite with WebMock

### Dependencies

- faraday >= 2.0, < 3.0
- faraday-retry ~> 2.0
