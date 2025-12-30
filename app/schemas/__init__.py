"""
Pydantic Schemas for Request/Response Validation
"""

from .booster_box import BoosterBoxCreate, BoosterBoxResponse, BoosterBoxListResponse
from .metrics import ManualMetricsInput, BulkManualMetricsInput, MetricsResponse
from .leaderboard import (
    LeaderboardBoxResponse,
    LeaderboardResponse,
    ResponseMeta,
    BoxMetricsSummary,
    SparklineDataPoint,
)
from .box_detail import (
    BoxDetailResponse,
    BoxDetailMetrics,
    TimeSeriesDataPoint,
    RankHistoryPoint,
)
from .image_processing import (
    ScreenshotUploadRequest,
    ScreenshotProcessingResponse,
    ManualExtractionSubmission,
)
from .sales_extraction import (
    IndividualSaleExtraction,
    ListingDataExtraction,
    BulkSalesExtraction,
    ListingItem,
)

__all__ = [
    # Admin schemas
    "BoosterBoxCreate",
    "BoosterBoxResponse",
    "BoosterBoxListResponse",
    "ManualMetricsInput",
    "BulkManualMetricsInput",
    "MetricsResponse",
    # Public API schemas
    "LeaderboardBoxResponse",
    "LeaderboardResponse",
    "ResponseMeta",
    "BoxMetricsSummary",
    "SparklineDataPoint",
    "BoxDetailResponse",
    "BoxDetailMetrics",
    "TimeSeriesDataPoint",
    "RankHistoryPoint",
    # Image processing schemas
    "ScreenshotUploadRequest",
    "ScreenshotProcessingResponse",
    "ManualExtractionSubmission",
    # Sales and listing extraction schemas
    "IndividualSaleExtraction",
    "ListingDataExtraction",
    "BulkSalesExtraction",
    "ListingItem",
]

