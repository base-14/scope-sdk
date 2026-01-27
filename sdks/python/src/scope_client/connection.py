"""HTTP connection handling for scope-client.

This module provides the Connection class that wraps httpx for making
HTTP requests to the Scope API with retry logic, error handling, and telemetry.
"""

import contextlib
import random
import time
from typing import Any, Optional

import httpx

from scope_client._telemetry import (
    ErrorInfo,
    RequestInfo,
    ResponseInfo,
    Telemetry,
    generate_request_id,
    redact_headers,
)
from scope_client._version import VERSION
from scope_client.configuration import Configuration
from scope_client.errors import (
    ConnectionError,
    TimeoutError,
    error_from_response,
)
from scope_client.token_manager import TokenManager

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class Connection:
    """HTTP connection handler for the Scope API.

    Manages HTTP requests with automatic retries, authentication,
    error handling, and optional telemetry.

    Args:
        config: Configuration instance with API settings.

    Example:
        >>> from scope_client.configuration import Configuration
        >>> config = Configuration(api_key="sk_test_123")
        >>> conn = Connection(config)
        >>> data = conn.get("prompts/my-prompt")
    """

    def __init__(self, config: Configuration) -> None:
        self._config = config
        self._client: Optional[httpx.Client] = None
        self._token_manager = TokenManager(config)

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client.

        Returns:
            Configured httpx.Client instance.
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._config.api_url,
                timeout=httpx.Timeout(
                    timeout=self._config.timeout,
                    connect=self._config.open_timeout,
                ),
                headers=self._default_headers(),
            )
        return self._client

    def _default_headers(self) -> dict[str, str]:
        """Get default headers for all requests.

        Returns:
            Dictionary of default headers.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"scope-client-python/{VERSION}",
        }

        if self._config.environment:
            headers["X-Scope-Environment"] = self._config.environment

        return headers

    def _get_auth_header(self) -> dict[str, str]:
        """Get current authorization header with fresh token.

        Returns:
            Dictionary with Authorization header.
        """
        return {"Authorization": f"Bearer {self._token_manager.get_access_token()}"}

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make a GET request.

        Args:
            path: API path (appended to base URL).
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On API errors.
            ConnectionError: On connection failures.
            TimeoutError: On request timeout.
        """
        return self._request("GET", path, params=params)

    def post(self, path: str, data: Optional[dict[str, Any]] = None) -> Any:
        """Make a POST request.

        Args:
            path: API path (appended to base URL).
            data: Optional JSON body.

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On API errors.
            ConnectionError: On connection failures.
            TimeoutError: On request timeout.
        """
        return self._request("POST", path, json=data)

    def put(self, path: str, data: Optional[dict[str, Any]] = None) -> Any:
        """Make a PUT request.

        Args:
            path: API path (appended to base URL).
            data: Optional JSON body.

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On API errors.
            ConnectionError: On connection failures.
            TimeoutError: On request timeout.
        """
        return self._request("PUT", path, json=data)

    def delete(self, path: str) -> Any:
        """Make a DELETE request.

        Args:
            path: API path (appended to base URL).

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On API errors.
            ConnectionError: On connection failures.
            TimeoutError: On request timeout.
        """
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            params: Query parameters.
            json: JSON body data.

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On API errors.
            ConnectionError: On connection failures.
            TimeoutError: On request timeout.
        """
        request_id = generate_request_id()
        url = f"{self._config.api_url}/{path}"
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts <= self._config.max_retries:
            attempts += 1
            start_time = time.time()

            try:
                # Emit request telemetry
                if self._config.telemetry_enabled:
                    self._emit_request_telemetry(request_id, method, url, json)

                response = self.client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                    headers={"X-Request-ID": request_id, **self._get_auth_header()},
                )

                elapsed_ms = (time.time() - start_time) * 1000

                # Emit response telemetry
                if self._config.telemetry_enabled:
                    self._emit_response_telemetry(request_id, response, elapsed_ms)

                # Handle response
                return self._handle_response(response)

            except httpx.TimeoutException as e:
                elapsed_ms = (time.time() - start_time) * 1000
                last_error = TimeoutError(
                    message=f"Request timed out after {self._config.timeout}s",
                    original_error=e,
                )

                if self._config.telemetry_enabled:
                    self._emit_error_telemetry(request_id, last_error, elapsed_ms)

                # Retry on timeout
                if attempts <= self._config.max_retries:
                    self._wait_for_retry(attempts)
                    continue
                raise last_error from e

            except httpx.ConnectError as e:
                elapsed_ms = (time.time() - start_time) * 1000
                last_error = ConnectionError(
                    message=f"Failed to connect to {self._config.base_url}",
                    original_error=e,
                )

                if self._config.telemetry_enabled:
                    self._emit_error_telemetry(request_id, last_error, elapsed_ms)

                # Retry on connection error
                if attempts <= self._config.max_retries:
                    self._wait_for_retry(attempts)
                    continue
                raise last_error from e

            except httpx.HTTPStatusError as e:
                elapsed_ms = (time.time() - start_time) * 1000
                response = e.response

                # Check if we should retry
                if (
                    response.status_code in RETRYABLE_STATUS_CODES
                    and attempts <= self._config.max_retries
                ):
                    # Get Retry-After header if present
                    retry_after = response.headers.get("Retry-After")
                    wait_time: float
                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            wait_time = self._calculate_backoff(attempts)
                    else:
                        wait_time = self._calculate_backoff(attempts)

                    time.sleep(wait_time)
                    continue

                # Not retryable or out of retries
                raise self._error_from_response(response) from e

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise ConnectionError("Request failed after all retries")

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response.

        Args:
            response: httpx Response object.

        Returns:
            Parsed JSON response data.

        Raises:
            ApiError: On API errors (4xx, 5xx).
        """
        if response.status_code >= 400:
            raise self._error_from_response(response)

        # Handle empty responses
        if not response.content:
            return None

        return response.json()

    def _error_from_response(self, response: httpx.Response) -> Exception:
        """Create appropriate error from HTTP response.

        Args:
            response: httpx Response object.

        Returns:
            Appropriate exception instance.
        """
        body = response.text
        error_code = None
        message = None
        request_id = response.headers.get("X-Request-ID")
        retry_after = None

        # Try to parse error details from JSON body
        try:
            data = response.json()
            if isinstance(data, dict):
                error_code = data.get("error", {}).get("code")
                message = data.get("error", {}).get("message")
        except Exception:
            pass

        # Get Retry-After for rate limit errors
        if response.status_code == 429:
            retry_after_header = response.headers.get("Retry-After")
            if retry_after_header:
                with contextlib.suppress(ValueError):
                    retry_after = int(retry_after_header)

        return error_from_response(
            status_code=response.status_code,
            body=body,
            error_code=error_code,
            request_id=request_id,
            message=message,
            retry_after=retry_after,
        )

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (1-based).

        Returns:
            Wait time in seconds.
        """
        base_delay = self._config.retry_base_delay
        max_delay = self._config.retry_max_delay

        # Exponential backoff: base * 2^(attempt-1)
        delay = base_delay * (2 ** (attempt - 1))

        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        delay += jitter

        # Cap at max delay
        result: float = min(delay, max_delay)
        return result

    def _wait_for_retry(self, attempt: int) -> None:
        """Wait before retrying a request.

        Args:
            attempt: Current attempt number (1-based).
        """
        wait_time = self._calculate_backoff(attempt)
        time.sleep(wait_time)

    def _emit_request_telemetry(
        self,
        request_id: str,
        method: str,
        url: str,
        body: Optional[dict[str, Any]] = None,
    ) -> None:
        """Emit telemetry for a request.

        Args:
            request_id: Unique request identifier.
            method: HTTP method.
            url: Full URL.
            body: Request body.
        """
        Telemetry.emit_request(
            RequestInfo(
                request_id=request_id,
                method=method,
                url=url,
                headers=redact_headers(self._default_headers()),
                body=body,
            )
        )

    def _emit_response_telemetry(
        self,
        request_id: str,
        response: httpx.Response,
        elapsed_ms: float,
    ) -> None:
        """Emit telemetry for a response.

        Args:
            request_id: Unique request identifier.
            response: HTTP response.
            elapsed_ms: Request duration in milliseconds.
        """
        try:
            body = response.json() if response.content else None
        except Exception:
            body = response.text

        Telemetry.emit_response(
            ResponseInfo(
                request_id=request_id,
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
                elapsed_ms=elapsed_ms,
            )
        )

    def _emit_error_telemetry(
        self,
        request_id: str,
        error: Exception,
        elapsed_ms: float,
    ) -> None:
        """Emit telemetry for an error.

        Args:
            request_id: Unique request identifier.
            error: The exception that occurred.
            elapsed_ms: Time elapsed before error.
        """
        Telemetry.emit_error(
            ErrorInfo(
                request_id=request_id,
                error=error,
                elapsed_ms=elapsed_ms,
            )
        )

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "Connection":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager and close connection."""
        self.close()
