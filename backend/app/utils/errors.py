from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union
import structlog

logger = structlog.get_logger()


class LuminaException(Exception):
    """Base exception for Lumina AI Agents"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class AgentExecutionError(LuminaException):
    """Agent execution failed"""

    def __init__(self, message: str, agent_id: str = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="AGENT_EXECUTION_ERROR",
        )
        self.agent_id = agent_id


class ModelRouterError(LuminaException):
    """Model routing failed"""

    def __init__(self, message: str, model: str = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="MODEL_ROUTER_ERROR",
        )
        self.model = model


class MemoryError(LuminaException):
    """Memory operation failed"""

    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="MEMORY_ERROR",
        )
        self.operation = operation


async def lumina_exception_handler(request: Request, exc: LuminaException):
    """Handle Lumina custom exceptions"""
    logger.error(
        "Lumina exception",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "path": request.url.path,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": request.url.path,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
                "path": request.url.path,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        "Unexpected exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "path": request.url.path,
            }
        },
    )


def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""
    app.add_exception_handler(LuminaException, lumina_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
