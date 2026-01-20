#!/usr/bin/env python3
"""Basic usage example for the Scope Client SDK.

This example demonstrates the basic functionality of the SDK including:
- Configuration
- Fetching prompts
- Rendering templates
- Using caching

Before running this example, set your API key:
    export SCOPE_API_KEY="sk_your_api_key"

Or modify the script to include your API key directly.
"""

import os

import scope_client
from scope_client import Telemetry, RequestInfo, ResponseInfo


def main() -> None:
    # Configure the SDK
    # The API key can be set via environment variable SCOPE_API_KEY
    # or passed directly to configure()
    api_key = os.environ.get("SCOPE_API_KEY")
    if not api_key:
        print("Please set SCOPE_API_KEY environment variable")
        print("Example: export SCOPE_API_KEY='sk_your_api_key'")
        return

    scope_client.configure(
        api_key=api_key,
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

    # Example 1: Fetch a prompt
    print("1. Fetching a prompt...")
    try:
        prompt = client.get_prompt("example-prompt")
        print(f"   Prompt: {prompt.name}")
        print(f"   ID: {prompt.id}")
        print(f"   Has production version: {prompt.has_production_version}")
    except scope_client.NotFoundError:
        print("   Prompt 'example-prompt' not found")
        print("   (This is expected if you haven't created this prompt)")

    # Example 2: Get production version and render
    print("\n2. Rendering a prompt...")
    try:
        version = client.get_prompt_production("greeting")
        print(f"   Content template: {version.content}")
        print(f"   Variables: {version.variables}")

        rendered = version.render({
            "name": "Alice",
            "greeting": "Hello",
        })
        print(f"   Rendered: {rendered}")
    except scope_client.NoProductionVersionError as e:
        print(f"   No production version for: {e.prompt_id}")
    except scope_client.NotFoundError:
        print("   Prompt 'greeting' not found")

    # Example 3: Using the render_prompt convenience method
    print("\n3. Using render_prompt method...")
    try:
        rendered = client.render_prompt(
            "greeting",
            {"name": "Bob", "greeting": "Hi"},
            version="latest",  # Can be "production", "latest", or a version ID
        )
        print(f"   Rendered: {rendered}")
    except (scope_client.NotFoundError, scope_client.NoProductionVersionError):
        print("   Prompt not found or no version available")

    # Example 4: Listing prompts
    print("\n4. Listing prompts...")
    try:
        result = client.list_prompts(page=1, per_page=5)
        print(f"   Total prompts: {result['meta'].get('total', 'unknown')}")
        for p in result["data"]:
            print(f"   - {p.name} ({p.id})")
    except scope_client.ApiError as e:
        print(f"   Error listing prompts: {e}")

    # Example 5: Cache demonstration
    print("\n5. Cache demonstration...")
    print("   First request (cache miss):")
    try:
        client.get_prompt("example-prompt")
    except scope_client.NotFoundError:
        pass

    print("   Second request (cache hit - no HTTP request):")
    try:
        client.get_prompt("example-prompt")
    except scope_client.NotFoundError:
        pass

    print("   Request with cache bypass:")
    try:
        client.get_prompt("example-prompt", cache=False)
    except scope_client.NotFoundError:
        pass

    # Example 6: Clear cache
    print("\n6. Clearing cache...")
    client.clear_cache()
    print("   Cache cleared")

    # Clean up
    client.close()
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
