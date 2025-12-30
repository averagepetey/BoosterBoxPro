"""
Error handling middleware for FastAPI
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import (
    BoosterBoxProError,
    BoxNotFoundError,
    InvalidDateError,
    MetricsNotFoundError,
    InvalidParameterError,
)

logger = logging.getLogger(__name__)


async def custom_exception_handler(request: Request, exc: BoosterBoxProError):
    """
    Handle custom BoosterBoxPro exceptions
    """
    status_code_map = {
        BoxNotFoundError: status.HTTP_404_NOT_FOUND,
        MetricsNotFoundError: status.HTTP_404_NOT_FOUND,
        InvalidDateError: status.HTTP_400_BAD_REQUEST,
        InvalidParameterError: status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.error(f"Custom exception: {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "detail": str(exc),
            "path": str(request.url.path),
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "detail": "Invalid request parameters",
            "errors": errors,
            "path": str(request.url.path),
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions (404, 400, etc.)
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "detail": exc.detail,
            "path": str(request.url.path),
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions (500 errors)
    """
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred. Please try again later.",
            "path": str(request.url.path),
        }
    )

