

class OffersAPIError(Exception):
    """Base exception for Offers SDK."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(f"Error: "
                         f"{status_code if status_code else 'N/A'} | {error_code if error_code else 'N/A'} | {message}")


class AuthenticationError(OffersAPIError):
    """401 Unauthorized"""

    def __init__(
        self,
        message: str = "Unauthorized access",
        *,
        status_code: int = 401,
        error_code: str = "AUTH_ERROR"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class NotFoundError(OffersAPIError):
    """404 Not Found"""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        status_code: int = 404,
        error_code: str = "NOT_FOUND"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class ConflictError(OffersAPIError):
    """409 Conflict"""

    def __init__(
        self,
        message: str = "Conflict detected",
        *,
        status_code: int = 409,
        error_code: str = "CONFLICT"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class ServerError(OffersAPIError):
    """500 Internal Server Error"""

    def __init__(
        self,
        message: str = "Internal server error",
        *,
        status_code: int = 500,
        error_code: str = "SERVER_ERROR"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class RateLimitError(OffersAPIError):
    """429 Rate Limit"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        status_code: int = 429,
        error_code: str = "RATE_LIMIT"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class TimeoutError(OffersAPIError):
    """408 Timeout"""

    def __init__(
        self,
        message: str = "Request timed out",
        *,
        status_code: int = 408,
        error_code: str = "TIMEOUT"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class PluginError(OffersAPIError):
    def __init__(
        self,
        message: str = "Plugin execution failed",
        *,
        status_code: int | None = None,
        error_code: str = "PLUGIN_ERROR"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class RequestExecutionError(OffersAPIError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class AuthRequestError(OffersAPIError):
    def __init__(
        self,
        message: str = "Authentication request failed",
        *,
        status_code: int | None = None,
        error_code: str = "AUTH_REQUEST"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)


class SDKConfigError(OffersAPIError):
    def __init__(
        self,
        message: str = "SDK configuration error",
        *,
        status_code: int | None = None,
        error_code: str = "SDK_CONFIG_ERROR"
    ):
        super().__init__(message, status_code=status_code, error_code=error_code)
