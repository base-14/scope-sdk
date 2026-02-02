#!/usr/bin/env python3
"""Error handling example for the Scope Client SDK.

This example demonstrates how to handle various errors that can occur
when using the SDK.

Before running this example, set your environment variables:
    export SCOPE_ORG_ID="your-org-id"
    export SCOPE_API_KEY="your-api-key"
    export SCOPE_API_SECRET="your-api-secret"
"""

import scope_client
from scope_client import (
    ApiKeyCredentials,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConnectionError,
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

    # Example 1: Configuration Error
    print("1. Configuration Error")
    print("-" * 40)
    try:
        scope_client.reset_configuration()
        # This will raise ConfigurationError because no credentials are configured
        client = scope_client.client()
    except ConfigurationError as e:
        print(f"   Caught ConfigurationError: {e}")
        print("   Solution: Set credentials via configure() or pass to client()")
    print()

    # Now configure properly for remaining examples
    try:
        credentials = ApiKeyCredentials.from_env()
        scope_client.configure(credentials=credentials)
        client = scope_client.client()
    except ConfigurationError:
        print("   Cannot continue - credentials not configured")
        return

    # Example 2: Not Found Error
    print("2. Not Found Error")
    print("-" * 40)
    try:
        version = client.get_prompt_version("nonexistent-prompt-12345")
    except NotFoundError as e:
        print(f"   Caught NotFoundError: {e.message}")
        print(f"   HTTP Status: {e.http_status}")
        print(f"   Request ID: {e.request_id}")
    except NoProductionVersionError as e:
        print(f"   Caught NoProductionVersionError: {e.message}")
    print()

    # Example 3: No Production Version Error
    print("3. No Production Version Error")
    print("-" * 40)
    try:
        version = client.get_prompt_version("prompt-without-production")
    except NoProductionVersionError as e:
        print(f"   Caught NoProductionVersionError: {e.message}")
        print(f"   Prompt ID: {e.prompt_id}")
        print("   Solution: Either publish a version to production or use label='latest'")
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
        rendered = mock_version.render(name="Alice")
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
        rendered = mock_version.render(
            name="Alice",
            unknown_var="value",
        )
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
        result = client.get_prompt_version("my-prompt")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
        time.sleep(e.retry_after)
        result = client.get_prompt_version("my-prompt")
    """)
    print()

    # Example 7: Generic error handling pattern
    print("7. Recommended Error Handling Pattern")
    print("-" * 40)
    print("""
    try:
        version = client.get_prompt_version("my-prompt")
        rendered = version.render(name="User")
        print(rendered)

    except AuthenticationError:
        print("Invalid API key. Check your credentials.")
        sys.exit(1)

    except AuthorizationError:
        print("Access denied. Check your permissions.")
        sys.exit(1)

    except NotFoundError:
        print("Prompt not found. Check the prompt ID.")

    except NoProductionVersionError:
        # Fallback to latest version
        print("No production version, using latest...")
        version = client.get_prompt_version("my-prompt", label="latest")
        rendered = version.render(name="User")

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
