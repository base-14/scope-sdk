"""Exception hierarchy for scope-client.

This module defines all exceptions that can be raised by the SDK.
All exceptions inherit from ScopeError for easy catching.
"""

from typing import Any, Optional


class ScopeError(Exception):
    """Base exception for all scope-client errors.

    Args:
        message: Human-readable error description.
        http_status: HTTP status code if applicable.
        http_body: Raw HTTP response body if applicable.
        error_code: Machine-readable error code from API.
        request_id: Request ID for debugging.
    """

    def __init__(
        self,
        message: str,
        http_status: Optional[int] = None,
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.http_body = http_body
        self.error_code = error_code
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.http_status:
            parts.append(f"HTTP Status: {self.http_status}")
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"http_status={self.http_status!r}, "
            f"error_code={self.error_code!r}, "
            f"request_id={self.request_id!r})"
        )


# Configuration Errors


class ConfigurationError(ScopeError):
    """Raised when there is a configuration problem."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingApiKeyError(ConfigurationError):
    """Raised when API key is not provided."""

    def __init__(self) -> None:
        super().__init__(
            "API key is required. Set SCOPE_API_KEY environment variable "
            "or pass api_key to configure()."
        )


# API Errors


class ApiError(ScopeError):
    """Base class for API-related errors."""

    pass


class AuthenticationError(ApiError):
    """Raised when authentication fails (401)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=401,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )


class AuthorizationError(ApiError):
    """Raised when authorization fails (403)."""

    def __init__(
        self,
        message: str = "Access denied. Insufficient permissions.",
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=403,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )


class NotFoundError(ApiError):
    """Raised when a resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found.",
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=404,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )


class ConflictError(ApiError):
    """Raised when there is a conflict (409)."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=409,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )


class RateLimitError(ApiError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please retry later.",
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=429,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )
        self.retry_after = retry_after

    def __repr__(self) -> str:
        base = super().__repr__()
        return base[:-1] + f", retry_after={self.retry_after!r})"


class ServerError(ApiError):
    """Raised when server returns 5xx error."""

    def __init__(
        self,
        message: str = "Server error. Please retry later.",
        http_status: int = 500,
        http_body: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            http_status=http_status,
            http_body=http_body,
            error_code=error_code,
            request_id=request_id,
        )


# Connection Errors


class ConnectionError(ScopeError):
    """Raised when connection to API fails."""

    def __init__(
        self,
        message: str = "Failed to connect to API.",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.original_error = original_error


class TimeoutError(ConnectionError):
    """Raised when request times out."""

    def __init__(
        self,
        message: str = "Request timed out.",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, original_error=original_error)


# Resource Errors


class ResourceError(ScopeError):
    """Base class for resource-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationError(ResourceError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.value = value

    def __repr__(self) -> str:
        return (
            f"ValidationError(message={self.message!r}, field={self.field!r}, value={self.value!r})"
        )


class RenderError(ResourceError):
    """Raised when template rendering fails."""

    def __init__(
        self,
        message: str,
        template: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.template = template


class MissingVariableError(RenderError):
    """Raised when required variables are missing during rendering."""

    def __init__(
        self,
        missing_variables: list[str],
        template: Optional[str] = None,
    ) -> None:
        self.missing_variables = missing_variables
        message = f"Missing required variables: {', '.join(missing_variables)}"
        super().__init__(message, template=template)

    def __repr__(self) -> str:
        return f"MissingVariableError(missing_variables={self.missing_variables!r})"


class NoProductionVersionError(ResourceError):
    """Raised when a prompt has no production version."""

    def __init__(self, prompt_id: str) -> None:
        self.prompt_id = prompt_id
        super().__init__(f"Prompt '{prompt_id}' has no production version.")

    def __repr__(self) -> str:
        return f"NoProductionVersionError(prompt_id={self.prompt_id!r})"


def error_from_response(
    status_code: int,
    body: Optional[str] = None,
    error_code: Optional[str] = None,
    request_id: Optional[str] = None,
    message: Optional[str] = None,
    retry_after: Optional[int] = None,
) -> ApiError:
    """Create appropriate error from HTTP response.

    Args:
        status_code: HTTP status code.
        body: Raw response body.
        error_code: Machine-readable error code.
        request_id: Request ID for debugging.
        message: Human-readable error message.
        retry_after: Retry-After header value for 429.

    Returns:
        Appropriate ApiError subclass instance.
    """
    error_classes = {
        401: AuthenticationError,
        403: AuthorizationError,
        404: NotFoundError,
        409: ConflictError,
        429: RateLimitError,
    }

    if status_code in error_classes:
        error_class = error_classes[status_code]
        kwargs: dict[str, Any] = {
            "http_body": body,
            "error_code": error_code,
            "request_id": request_id,
        }
        if message:
            kwargs["message"] = message
        if status_code == 429 and retry_after is not None:
            kwargs["retry_after"] = retry_after
        result: ApiError = error_class(**kwargs)
        return result

    if 500 <= status_code < 600:
        return ServerError(
            message=message or "Server error. Please retry later.",
            http_status=status_code,
            http_body=body,
            error_code=error_code,
            request_id=request_id,
        )

    return ApiError(
        message=message or f"API error (HTTP {status_code})",
        http_status=status_code,
        http_body=body,
        error_code=error_code,
        request_id=request_id,
    )
