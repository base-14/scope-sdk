"""Telemetry hooks for request/response tracking.

This module provides hooks for observing HTTP requests and responses
made by the SDK. Useful for logging, metrics, and debugging.
"""

import contextlib
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class RequestInfo:
    """Information about an outgoing HTTP request.

    Attributes:
        request_id: Unique identifier for this request.
        method: HTTP method (GET, POST, etc.).
        url: Full URL of the request.
        headers: Request headers (authorization header is redacted).
        body: Request body if applicable.
    """

    request_id: str
    method: str
    url: str
    headers: dict[str, str]
    body: Optional[Any] = None


@dataclass
class ResponseInfo:
    """Information about an HTTP response.

    Attributes:
        request_id: Unique identifier matching the request.
        status_code: HTTP status code.
        headers: Response headers.
        body: Parsed response body.
        elapsed_ms: Request duration in milliseconds.
    """

    request_id: str
    status_code: int
    headers: dict[str, str]
    body: Optional[Any] = None
    elapsed_ms: float = 0.0


@dataclass
class ErrorInfo:
    """Information about a request error.

    Attributes:
        request_id: Unique identifier matching the request.
        error: The exception that occurred.
        elapsed_ms: Time elapsed before the error in milliseconds.
    """

    request_id: str
    error: Exception
    elapsed_ms: float = 0.0


# Type aliases for callback functions
OnRequestCallback = Callable[[RequestInfo], None]
OnResponseCallback = Callable[[ResponseInfo], None]
OnErrorCallback = Callable[[ErrorInfo], None]


class Telemetry:
    """Global telemetry manager for request/response hooks.

    This class provides a centralized way to register callbacks that are
    invoked on HTTP requests, responses, and errors. Useful for logging,
    metrics collection, and debugging.

    Example:
        >>> def log_request(info: RequestInfo):
        ...     print(f"Request {info.request_id}: {info.method} {info.url}")
        ...
        >>> Telemetry.on_request(log_request)

        >>> def log_response(info: ResponseInfo):
        ...     print(f"Response {info.request_id}: {info.status_code} in {info.elapsed_ms}ms")
        ...
        >>> Telemetry.on_response(log_response)
    """

    _lock: threading.Lock = threading.Lock()
    _request_callbacks: list[OnRequestCallback] = []
    _response_callbacks: list[OnResponseCallback] = []
    _error_callbacks: list[OnErrorCallback] = []

    @classmethod
    def on_request(cls, callback: OnRequestCallback) -> None:
        """Register a callback for request events.

        Args:
            callback: Function to call with RequestInfo on each request.
        """
        with cls._lock:
            cls._request_callbacks.append(callback)

    @classmethod
    def on_response(cls, callback: OnResponseCallback) -> None:
        """Register a callback for response events.

        Args:
            callback: Function to call with ResponseInfo on each response.
        """
        with cls._lock:
            cls._response_callbacks.append(callback)

    @classmethod
    def on_error(cls, callback: OnErrorCallback) -> None:
        """Register a callback for error events.

        Args:
            callback: Function to call with ErrorInfo on errors.
        """
        with cls._lock:
            cls._error_callbacks.append(callback)

    @classmethod
    def clear_callbacks(cls) -> None:
        """Remove all registered callbacks."""
        with cls._lock:
            cls._request_callbacks.clear()
            cls._response_callbacks.clear()
            cls._error_callbacks.clear()

    @classmethod
    def emit_request(cls, info: RequestInfo) -> None:
        """Emit a request event to all registered callbacks.

        Args:
            info: Request information.
        """
        with cls._lock:
            callbacks = cls._request_callbacks.copy()

        for callback in callbacks:
            with contextlib.suppress(Exception):
                callback(info)

    @classmethod
    def emit_response(cls, info: ResponseInfo) -> None:
        """Emit a response event to all registered callbacks.

        Args:
            info: Response information.
        """
        with cls._lock:
            callbacks = cls._response_callbacks.copy()

        for callback in callbacks:
            with contextlib.suppress(Exception):
                callback(info)

    @classmethod
    def emit_error(cls, info: ErrorInfo) -> None:
        """Emit an error event to all registered callbacks.

        Args:
            info: Error information.
        """
        with cls._lock:
            callbacks = cls._error_callbacks.copy()

        for callback in callbacks:
            with contextlib.suppress(Exception):
                callback(info)

    @classmethod
    def has_callbacks(cls) -> bool:
        """Check if any callbacks are registered.

        Returns:
            True if any callbacks are registered, False otherwise.
        """
        with cls._lock:
            return bool(cls._request_callbacks or cls._response_callbacks or cls._error_callbacks)


def generate_request_id() -> str:
    """Generate a unique request ID.

    Returns:
        A UUID string for request tracking.
    """
    return str(uuid.uuid4())


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redact sensitive values from headers for telemetry.

    Args:
        headers: Original headers dictionary.

    Returns:
        Headers with sensitive values redacted.
    """
    sensitive_keys = {"authorization", "x-api-key", "api-key"}
    redacted = {}

    for key, value in headers.items():
        if key.lower() in sensitive_keys:
            # Show the type of auth but not the actual value
            if value.lower().startswith("bearer "):
                redacted[key] = "Bearer [REDACTED]"
            else:
                redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value

    return redacted
