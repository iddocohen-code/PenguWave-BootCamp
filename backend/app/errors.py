"""Custom exceptions and error handling for consistent API error responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error. Caught by middleware and returned as {"error": "..."}."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AppError):
    """401: missing or invalid authentication."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class AuthorizationError(AppError):
    """403: authenticated but not authorized for this resource."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class NotFoundError(AppError):
    """404: resource not found."""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, 404)


class ValidationError(AppError):
    """400: invalid request body or parameters."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400)


def register_error_handlers(app: FastAPI):
    """Register global error handlers so all errors return {"error": "..."}."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500, content={"error": "Internal server error"}
        )
