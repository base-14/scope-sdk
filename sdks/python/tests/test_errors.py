"""Tests for error classes."""

from scope_client.errors import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConflictError,
    ConnectionError,
    MissingApiKeyError,
    MissingVariableError,
    NoProductionVersionError,
    NotFoundError,
    RateLimitError,
    RenderError,
    ResourceError,
    ScopeError,
    ServerError,
    TimeoutError,
    ValidationError,
    error_from_response,
)


class TestScopeError:
    """Tests for base ScopeError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = ScopeError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.http_status is None
        assert error.http_body is None
        assert error.error_code is None
        assert error.request_id is None

    def test_error_with_metadata(self):
        """Test error with all metadata."""
        error = ScopeError(
            "API error",
            http_status=500,
            http_body='{"error": "internal"}',
            error_code="INTERNAL_ERROR",
            request_id="req-123",
        )
        assert error.http_status == 500
        assert error.error_code == "INTERNAL_ERROR"
        assert error.request_id == "req-123"
        assert "HTTP Status: 500" in str(error)
        assert "Error Code: INTERNAL_ERROR" in str(error)
        assert "Request ID: req-123" in str(error)

    def test_error_repr(self):
        """Test error representation."""
        error = ScopeError("test", http_status=404, error_code="NOT_FOUND")
        repr_str = repr(error)
        assert "ScopeError" in repr_str
        assert "404" in repr_str
        assert "NOT_FOUND" in repr_str


class TestConfigurationErrors:
    """Tests for configuration error classes."""

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid config")
        assert isinstance(error, ScopeError)
        assert str(error) == "Invalid config"

    def test_missing_api_key_error(self):
        """Test MissingApiKeyError."""
        error = MissingApiKeyError()
        assert isinstance(error, ConfigurationError)
        assert "API key is required" in str(error)
        assert "SCOPE_API_KEY" in str(error)


class TestApiErrors:
    """Tests for API error classes."""

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError()
        assert isinstance(error, ApiError)
        assert error.http_status == 401
        assert "Authentication failed" in str(error)

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError(
            message="Invalid API key",
            error_code="INVALID_KEY",
            request_id="req-123",
        )
        assert str(error).startswith("Invalid API key")
        assert error.error_code == "INVALID_KEY"

    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError()
        assert error.http_status == 403
        assert "Access denied" in str(error)

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError()
        assert error.http_status == 404
        assert "not found" in str(error).lower()

    def test_conflict_error(self):
        """Test ConflictError."""
        error = ConflictError()
        assert error.http_status == 409
        assert "conflict" in str(error).lower()

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(retry_after=60)
        assert error.http_status == 429
        assert error.retry_after == 60
        assert "retry_after=60" in repr(error)

    def test_server_error(self):
        """Test ServerError."""
        error = ServerError(http_status=503)
        assert error.http_status == 503
        assert isinstance(error, ApiError)


class TestConnectionErrors:
    """Tests for connection error classes."""

    def test_connection_error(self):
        """Test ConnectionError."""
        original = Exception("network failure")
        error = ConnectionError("Failed to connect", original_error=original)
        assert isinstance(error, ScopeError)
        assert error.original_error is original

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError()
        assert isinstance(error, ConnectionError)
        assert "timed out" in str(error).lower()


class TestResourceErrors:
    """Tests for resource error classes."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid value", field="name", value="")
        assert isinstance(error, ResourceError)
        assert error.field == "name"
        assert error.value == ""

    def test_render_error(self):
        """Test RenderError."""
        error = RenderError("Render failed", template="{{name}}")
        assert isinstance(error, ResourceError)
        assert error.template == "{{name}}"

    def test_missing_variable_error(self):
        """Test MissingVariableError."""
        error = MissingVariableError(["name", "email"])
        assert isinstance(error, RenderError)
        assert error.missing_variables == ["name", "email"]
        assert "name" in str(error)
        assert "email" in str(error)

    def test_no_production_version_error(self):
        """Test NoProductionVersionError."""
        error = NoProductionVersionError("my-prompt")
        assert isinstance(error, ResourceError)
        assert error.prompt_id == "my-prompt"
        assert "my-prompt" in str(error)
        assert "no production version" in str(error).lower()


class TestErrorFromResponse:
    """Tests for error_from_response factory function."""

    def test_401_error(self):
        """Test 401 creates AuthenticationError."""
        error = error_from_response(401)
        assert isinstance(error, AuthenticationError)
        assert error.http_status == 401

    def test_403_error(self):
        """Test 403 creates AuthorizationError."""
        error = error_from_response(403)
        assert isinstance(error, AuthorizationError)

    def test_404_error(self):
        """Test 404 creates NotFoundError."""
        error = error_from_response(404, message="Prompt not found")
        assert isinstance(error, NotFoundError)
        assert "Prompt not found" in str(error)

    def test_409_error(self):
        """Test 409 creates ConflictError."""
        error = error_from_response(409)
        assert isinstance(error, ConflictError)

    def test_429_error(self):
        """Test 429 creates RateLimitError with retry_after."""
        error = error_from_response(429, retry_after=120)
        assert isinstance(error, RateLimitError)
        assert error.retry_after == 120

    def test_500_error(self):
        """Test 500 creates ServerError."""
        error = error_from_response(500)
        assert isinstance(error, ServerError)
        assert error.http_status == 500

    def test_502_error(self):
        """Test 502 creates ServerError."""
        error = error_from_response(502)
        assert isinstance(error, ServerError)
        assert error.http_status == 502

    def test_unknown_status(self):
        """Test unknown status creates generic ApiError."""
        error = error_from_response(418, message="I'm a teapot")
        assert isinstance(error, ApiError)
        assert error.http_status == 418
        assert "teapot" in str(error)

    def test_with_full_metadata(self):
        """Test error with all metadata."""
        error = error_from_response(
            404,
            body='{"error": {"code": "NOT_FOUND"}}',
            error_code="NOT_FOUND",
            request_id="req-xyz",
            message="Resource not found",
        )
        assert error.http_body == '{"error": {"code": "NOT_FOUND"}}'
        assert error.error_code == "NOT_FOUND"
        assert error.request_id == "req-xyz"
