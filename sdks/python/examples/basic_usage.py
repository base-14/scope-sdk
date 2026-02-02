#!/usr/bin/env python3
"""Basic usage example for the Scope Client SDK.

This example demonstrates the basic functionality of the SDK including:
- Configuration
- Fetching prompt versions
- Rendering templates
- Using caching

Before running this example, set your environment variables:
    export SCOPE_ORG_ID="your-org-id"
    export SCOPE_API_KEY="your-api-key"
    export SCOPE_API_SECRET="your-api-secret"

Or modify the script to include your credentials directly.
"""

import scope_client
from scope_client import ApiKeyCredentials, Telemetry, RequestInfo, ResponseInfo


def main() -> None:
    # Configure the SDK using credentials from environment
    try:
        credentials = ApiKeyCredentials.from_env()
    except scope_client.ConfigurationError:
        print("Please set SCOPE_ORG_ID, SCOPE_API_KEY, and SCOPE_API_SECRET environment variables")
        return

    scope_client.configure(
        credentials=credentials,
        cache_enabled=True,
        cache_ttl=300,  # Cache for 5 minutes
    )

    # Optional: Set up telemetry to see requests
    def log_request(info: RequestInfo) -> None:
        print(f"[Request] {info.method} {info.url}")

    def log_response(info: ResponseInfo) -> None:
        print(f"[Response] {info.status_code} in {info.elapsed_ms:.2f}ms")

    Telemetry.on_request(log_request)
    Telemetry.on_response(log_response)

    # Create a client
    client = scope_client.client()

    print("\n=== Scope Client SDK Basic Usage ===\n")

    # Example 1: Get production version and render
    print("1. Getting production version...")
    try:
        version = client.get_prompt_version("greeting")
        print(f"   Content template: {version.content}")
        print(f"   Variables: {version.variables}")

        rendered = version.render(
            name="Alice",
            greeting="Hello",
        )
        print(f"   Rendered: {rendered}")
    except scope_client.NoProductionVersionError as e:
        print(f"   No production version for: {e.prompt_id}")
    except scope_client.NotFoundError:
        print("   Prompt 'greeting' not found")
    print()

    # Example 2: Using the render_prompt convenience method
    print("2. Using render_prompt method...")
    try:
        rendered = client.render_prompt(
            "greeting",
            {"name": "Bob", "greeting": "Hi"},
            label="latest",
        )
        print(f"   Rendered: {rendered}")
    except (scope_client.NotFoundError, scope_client.NoProductionVersionError):
        print("   Prompt not found or no version available")
    print()

    # Example 3: Cache demonstration
    print("3. Cache demonstration...")
    print("   First request (cache miss):")
    try:
        client.get_prompt_version("greeting")
    except (scope_client.NotFoundError, scope_client.NoProductionVersionError):
        pass

    print("   Second request (cache hit - no HTTP request):")
    try:
        client.get_prompt_version("greeting")
    except (scope_client.NotFoundError, scope_client.NoProductionVersionError):
        pass

    print("   Request with cache bypass:")
    try:
        client.get_prompt_version("greeting", cache=False)
    except (scope_client.NotFoundError, scope_client.NoProductionVersionError):
        pass
    print()

    # Example 4: Clear cache
    print("4. Clearing cache...")
    client.clear_cache()
    print("   Cache cleared")

    # Clean up
    client.close()
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
