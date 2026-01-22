"""
Pydantic Schemas for Request/Response Validation
"""

from .image_processing import (
    ScreenshotUploadRequest,
    ScreenshotProcessingResponse,
    ManualExtractionSubmission,
    DuplicateCheckResponse,
)

__all__ = [
    # Image processing schemas
    "ScreenshotUploadRequest",
    "ScreenshotProcessingResponse",
    "ManualExtractionSubmission",
    "DuplicateCheckResponse",
]
