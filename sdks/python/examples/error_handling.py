#!/usr/bin/env python3
"""Error handling example for the Scope Client SDK.

This example demonstrates how to handle various errors that can occur
when using the SDK.

Before running this example, set your API key:
    export SCOPE_API_KEY="sk_your_api_key"
"""

import os
import sys

import scope_client
from scope_client import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    MissingApiKeyError,
    MissingVariableError,
    NoProductionVersionError,
    NotFoundError,
    RateLimitError,
    ScopeError,
    ServerError,
    TimeoutError,
    ValidationError,
)


def demonstrate_error_handling() -> None:
    """Demonstrate various error handling scenarios."""

    # Example 1: Missing API Key Error
    print("1. Missing API Key Error")
    print("-" * 40)
    try:
        scope_client.reset_configuration()
        # Clear any environment variable
        if "SCOPE_API_KEY" in os.environ:
            del os.environ["SCOPE_API_KEY"]
        # This will raise MissingApiKeyError
        client = scope_client.client()
    except MissingApiKeyError as e:
        print(f"   Caught MissingApiKeyError: {e}")
        print("   Solution: Set SCOPE_API_KEY environment variable or pass api_key to configure()")
    print()

    # Now configure properly for remaining examples
    api_key = os.environ.get("SCOPE_API_KEY", "sk_test_key")
    scope_client.configure(api_key=api_key)
    client = scope_client.client()

    # Example 2: Not Found Error
    print("2. Not Found Error")
    print("-" * 40)
    try:
        prompt = client.get_prompt("nonexistent-prompt-12345")
    except NotFoundError as e:
        print(f"   Caught NotFoundError: {e.message}")
        print(f"   HTTP Status: {e.http_status}")
        print(f"   Request ID: {e.request_id}")
    print()

    # Example 3: No Production Version Error
    print("3. No Production Version Error")
    print("-" * 40)
    try:
        version = client.get_prompt_production("prompt-without-production")
    except NoProductionVersionError as e:
        print(f"   Caught NoProductionVersionError: {e.message}")
        print(f"   Prompt ID: {e.prompt_id}")
        print("   Solution: Either publish a version to production or use get_prompt_latest()")
    except NotFoundError:
        print("   (Prompt not found - this is expected in the demo)")
    print()

    # Example 4: Missing Variable Error
    print("4. Missing Variable Error")
    print("-" * 40)
    try:
        # Simulate a version with variables
        from scope_client.resources import PromptVersion

        mock_version = PromptVersion({
            "id": "v1",
            "prompt_id": "test",
            "version_number": 1,
            "content": "Hello, {{name}}! Your order {{order_id}} is ready.",
            "variables": ["name", "order_id"],
            "status": "published",
            "is_production": True,
        })

        # Try to render without all variables
        rendered = mock_version.render({"name": "Alice"})
    except MissingVariableError as e:
        print(f"   Caught MissingVariableError: {e.message}")
        print(f"   Missing variables: {e.missing_variables}")
        print("   Solution: Provide all required variables")
    print()

    # Example 5: Validation Error (unknown variables)
    print("5. Validation Error (unknown variables)")
    print("-" * 40)
    try:
        from scope_client.resources import PromptVersion

        mock_version = PromptVersion({
            "id": "v1",
            "prompt_id": "test",
            "version_number": 1,
            "content": "Hello, {{name}}!",
            "variables": ["name"],
            "status": "published",
        })

        # Try to render with unknown variables
        rendered = mock_version.render({
            "name": "Alice",
            "unknown_var": "value",
        })
    except ValidationError as e:
        print(f"   Caught ValidationError: {e.message}")
        print("   Solution: Only provide declared variables")
    print()

    # Example 6: Handling Rate Limit Errors
    print("6. Rate Limit Error Handling (simulated)")
    print("-" * 40)
    print("   In production, you might handle rate limits like this:")
    print("""
    try:
        result = client.get_prompt("my-prompt")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
        time.sleep(e.retry_after)
        result = client.get_prompt("my-prompt")
    """)
    print()

    # Example 7: Generic error handling pattern
    print("7. Recommended Error Handling Pattern")
    print("-" * 40)
    print("""
    try:
        version = client.get_prompt_production("my-prompt")
        rendered = version.render({"name": "User"})
        print(rendered)

    except AuthenticationError:
        print("Invalid API key. Check your SCOPE_API_KEY.")
        sys.exit(1)

    except AuthorizationError:
        print("Access denied. Check your permissions.")
        sys.exit(1)

    except NotFoundError:
        print("Prompt not found. Check the prompt ID.")

    except NoProductionVersionError:
        # Fallback to latest version
        print("No production version, using latest...")
        version = client.get_prompt_latest("my-prompt")
        rendered = version.render({"name": "User"})

    except MissingVariableError as e:
        print(f"Missing variables: {e.missing_variables}")

    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")

    except ConnectionError:
        print("Network error. Check your connection.")

    except TimeoutError:
        print("Request timed out. Try again later.")

    except ServerError:
        print("Server error. Try again later.")

    except ScopeError as e:
        # Catch-all for any other SDK errors
        print(f"Unexpected error: {e}")
    """)

    client.close()


def main() -> None:
    print("=" * 50)
    print("Scope Client SDK - Error Handling Examples")
    print("=" * 50)
    print()

    demonstrate_error_handling()

    print("=" * 50)
    print("Error handling demonstration complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
