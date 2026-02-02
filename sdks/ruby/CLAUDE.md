# CLAUDE.md

Development guidelines for AI assistants working on the Scope Ruby SDK.

## Development Philosophy

- Simplicity: Write simple, idiomatic Ruby code
- Readability: Follow Ruby style guides
- Thread Safety: All shared state must be thread-safe
- Testability: Design for easy unit testing
- Minimal Dependencies: Only essential gems

## Way of Working

- Start with minimal functionality, verify with tests
- Run RuboCop after each change: `make lint`
- Follow Test-Driven Development (write failing test first)
- Run tests before committing: `make test`
- Use trunk-based development with git
- All build commands through Makefile
- Do not add "Generated with" or "Co-Authored-By" lines to commits

## Ruby Specific Instructions

1. Use Bundler for dependency management
2. Use RuboCop for linting (run `make lint-fix` to auto-fix)
3. Use RSpec for testing
4. Use YARD for documentation
5. Target Ruby 2.7+ compatibility
6. Use frozen_string_literal pragma in all files
7. Follow Ruby style guide: https://rubystyle.guide/

## Code Style

- 2 spaces for indentation
- Use `frozen_string_literal: true` in all files
- Prefer `&&` and `||` over `and` and `or`
- Use `?` suffix for predicate methods returning boolean
- Document public methods with YARD annotations
- Keep methods under 20 lines where possible
- Max line length: 120 characters

## Testing Conventions

- Use RSpec with `expect` syntax
- One assertion per example when practical
- Use WebMock for HTTP stubbing
- Test both success and error scenarios
- Aim for 80%+ code coverage
- All tests should be in `spec/` directory

Example test structure:

```ruby
RSpec.describe ScopeClient::Client do
  describe "#get_prompt_version" do
    context "when prompt exists" do
      it "returns the production version by default" do
        # test implementation
      end
    end

    context "when production version does not exist" do
      it "raises NoProductionVersionError" do
        # test implementation
      end
    end
  end
end
```

## Common Commands

```bash
make install       # Install dependencies
make test          # Run tests
make test-coverage # Run tests with coverage
make lint          # Run linter
make lint-fix      # Auto-fix lint issues
make build         # Build gem
make docs          # Generate documentation
make console       # Interactive console
make ci            # Run full CI pipeline
```

## Thread Safety

- Use `Monitor` or `Mutex` for mutable shared state
- Configuration and Cache classes must be thread-safe
- Avoid class-level mutable state
- Document thread-safety guarantees in YARD comments

## Error Handling

- All errors inherit from `ScopeClient::Error`
- Include HTTP status and error code when available
- Provide meaningful error messages
- Use specific error classes for different failure modes

## Project Structure

```
lib/
├── scope_client.rb              # Main entry point
└── scope_client/
    ├── version.rb               # Version constant
    ├── configuration.rb         # Thread-safe configuration
    ├── client.rb                # Main client class
    ├── connection.rb            # Faraday HTTP wrapper
    ├── errors.rb                # Error hierarchy
    ├── cache.rb                 # Thread-safe cache
    ├── renderer.rb              # Variable substitution
    ├── middleware/
    │   ├── authentication.rb    # Bearer token auth
    │   └── telemetry.rb         # Request/response hooks
    └── resources/
        ├── base.rb              # Base resource class
        ├── prompt.rb            # Prompt resource
        └── prompt_version.rb    # Version resource
```

## CI/CD

- GitHub Actions for CI/CD
- Workflow location: `../../.github/workflows/scope-ruby-sdk-*.yml`
- Test matrix: Ruby 2.7, 3.0, 3.1, 3.2, 3.3
- Release triggered by `ruby-v*` tags

## API Reference

The SDK maps to these Scope API endpoints:

| SDK Method | HTTP Endpoint |
|------------|---------------|
| `get_prompt(name)` | GET /prompts/{name} |
| `get_prompt_version(name)` | GET /prompts/{name}/production |
| `get_prompt_version(name, label: :latest)` | GET /prompts/{name}/latest |
| `get_prompt_version(name, version: vid)` | GET /prompts/{name}/versions/{vid} |
| `list_prompts(**params)` | GET /prompts |
