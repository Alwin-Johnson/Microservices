from fastapi import HTTPException


class PlatformError(HTTPException):
    """Base exception for all platform-specific errors."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(PlatformError):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ValidationError(PlatformError):
    """Invalid input."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=400, detail=detail)


class ServiceUnavailableError(PlatformError):
    """Service is temporarily unavailable."""

    def __init__(self, detail: str = "Service unavailable"):
        super().__init__(status_code=503, detail=detail)
