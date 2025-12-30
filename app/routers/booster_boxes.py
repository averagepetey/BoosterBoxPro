"""
Public Booster Boxes Router
Public API endpoints for leaderboard, box details, and analytics
"""

from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.leaderboard import (
    LeaderboardResponse,
    LeaderboardBoxResponse,
    ResponseMeta,
    BoxMetricsSummary,
    SparklineDataPoint,
)
from app.schemas.box_detail import (
    BoxDetailResponse,
    BoxDetailMetrics,
    TimeSeriesDataPoint,
    RankHistoryPoint,
)
from app.services.leaderboard_service import LeaderboardService
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository

router = APIRouter(prefix="/booster-boxes", tags=["booster-boxes"])


def format_leaderboard_box(
    box,
    metrics,
    rank: int,
    rank_change_info: Optional[dict] = None
) -> LeaderboardBoxResponse:
    """Format box and metrics into LeaderboardBoxResponse"""
    
    # Build metrics summary
    metrics_summary = BoxMetricsSummary(
        floor_price_usd=metrics.floor_price_usd,
        floor_price_1d_change_pct=metrics.floor_price_1d_change_pct,
        daily_volume_usd=metrics.unified_volume_usd,
        unified_volume_7d_ema=metrics.unified_volume_7d_ema,
        units_sold_count=int(metrics.boxes_sold_per_day) if metrics.boxes_sold_per_day else None,
        active_listings_count=metrics.active_listings_count,
        listed_percentage=metrics.listed_percentage,
        estimated_total_supply=box.estimated_total_supply,
        liquidity_score=metrics.liquidity_score,
        days_to_20pct_increase=metrics.days_to_20pct_increase,
        expected_days_to_sell=metrics.expected_days_to_sell,
        price_sparkline_1d=None,  # Will be added if requested
    )
    
    return LeaderboardBoxResponse(
        id=box.id,
        rank=rank,
        rank_change_direction=rank_change_info.get("direction") if rank_change_info else None,
        rank_change_amount=rank_change_info.get("amount") if rank_change_info else None,
        product_name=box.product_name,
        set_name=box.set_name,
        game_type=box.game_type,
        image_url=box.image_url,
        metrics=metrics_summary,
        reprint_risk=box.reprint_risk,
        metric_date=metrics.metric_date,
    )


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    sort: str = Query(default="unified_volume_7d_ema", description="Field to sort by"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    date_param: Optional[date] = Query(default=None, alias="date", description="Date for metrics (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get leaderboard of booster boxes
    
    Returns ranked list of booster boxes sorted by the specified field.
    Default sort is by 7-day EMA volume (highest first).
    """
    leaderboard_service = LeaderboardService(db)
    
    # Get ranked boxes
    ranked_results = await leaderboard_service.get_ranked_boxes(
        target_date=date_param,
        sort_by=sort,
        sort_direction="desc",  # Default to descending for volume-based sorts
        limit=limit,
        offset=offset
    )
    
    # Format response
    leaderboard_boxes = []
    for box, metrics, rank, rank_change_info in ranked_results:
        leaderboard_box = format_leaderboard_box(box, metrics, rank, rank_change_info)
        leaderboard_boxes.append(leaderboard_box)
    
    # Get total count
    all_metrics = await UnifiedMetricsRepository.get_latest_for_all_boxes(db, date_param)
    total = len(all_metrics)
    
    return LeaderboardResponse(
        data=leaderboard_boxes,
        meta=ResponseMeta(
            total=total,
            sort=sort,
            sort_direction="desc",
            date=date_param,
            limit=limit,
            offset=offset
        )
    )


@router.get("/{box_id}", response_model=BoxDetailResponse)
async def get_box_detail(
    box_id: UUID,
    date_param: Optional[date] = Query(default=None, alias="date", description="Date for metrics (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed analytics for a specific booster box
    
    Returns comprehensive metrics, time-series data, and advanced analytics.
    This is the endpoint for the detail page accessed by clicking a box from the leaderboard.
    """
    # Get box
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Get metrics for specified date or latest
    if date_param:
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(db, box_id, date_param)
    else:
        metrics = await UnifiedMetricsRepository.get_latest_for_box(db, box_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found for this box")
    
    # Get rank
    leaderboard_service = LeaderboardService(db)
    rank = await leaderboard_service.get_box_rank(box_id, metrics.metric_date)
    
    # Get rank change
    rank_change_info = await leaderboard_service._calculate_rank_change(
        box_id,
        metrics.metric_date
    )
    
    # Get time-series data (last 30 days)
    end_date = metrics.metric_date
    start_date = end_date - timedelta(days=30)
    time_series_metrics = await UnifiedMetricsRepository.get_by_box_date_range(
        db, box_id, start_date, end_date
    )
    
    time_series_data = []
    for ts_metric in time_series_metrics:
        time_series_data.append(TimeSeriesDataPoint(
            date=ts_metric.metric_date,
            floor_price_usd=ts_metric.floor_price_usd,
            volume=ts_metric.unified_volume_usd,
            listings_count=ts_metric.active_listings_count,
            sales_count=int(ts_metric.boxes_sold_per_day) if ts_metric.boxes_sold_per_day else None,
            market_cap=ts_metric.visible_market_cap_usd,
        ))
    
    # Get rank history (last 30 days)
    rank_history_list = await UnifiedMetricsRepository.get_rank_history(
        db, box_id, start_date, end_date
    )
    rank_history = [
        RankHistoryPoint(
            date=rh["date"],
            rank=rh["rank"],
            rank_change=rh.get("rank_change")
        )
        for rh in rank_history_list
    ]
    
    # Build detailed metrics
    detail_metrics = BoxDetailMetrics(
        floor_price_usd=metrics.floor_price_usd,
        floor_price_1d_change_pct=metrics.floor_price_1d_change_pct,
        daily_volume_usd=metrics.unified_volume_usd,
        unified_volume_7d_ema=metrics.unified_volume_7d_ema,
        unified_volume_30d_sma=None,  # Not stored in model yet (can be calculated if needed)
        units_sold_count=int(metrics.boxes_sold_per_day) if metrics.boxes_sold_per_day else None,
        active_listings_count=metrics.active_listings_count,
        listed_percentage=metrics.listed_percentage,
        estimated_total_supply=box.estimated_total_supply,
        liquidity_score=metrics.liquidity_score,
        days_to_20pct_increase=metrics.days_to_20pct_increase,
        expected_days_to_sell=metrics.expected_days_to_sell,
        visible_market_cap_usd=metrics.visible_market_cap_usd,
        momentum_score=metrics.momentum_score,
        boxes_sold_per_day=metrics.boxes_sold_per_day,
        boxes_sold_30d_avg=metrics.boxes_sold_30d_avg,
        price_sparkline_1d=None,
    )
    
    return BoxDetailResponse(
        id=box.id,
        product_name=box.product_name,
        set_name=box.set_name,
        game_type=box.game_type,
        image_url=box.image_url,
        release_date=box.release_date,
        reprint_risk=box.reprint_risk,
        estimated_total_supply=box.estimated_total_supply,
        rank=rank,
        rank_change_direction=rank_change_info.get("direction") if rank_change_info else None,
        rank_change_amount=rank_change_info.get("amount") if rank_change_info else None,
        metrics=detail_metrics,
        metric_date=metrics.metric_date,
        time_series_data=time_series_data,
        rank_history=rank_history,
    )


@router.get("/{box_id}/time-series", response_model=List[TimeSeriesDataPoint])
async def get_time_series(
    box_id: UUID,
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time-series data for a booster box
    
    Returns historical daily metrics over a date range.
    """
    # Verify box exists
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Default to last 30 days if not specified
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get metrics
    metrics_list = await UnifiedMetricsRepository.get_by_box_date_range(
        db, box_id, start_date, end_date
    )
    
    time_series_data = []
    for metric in metrics_list:
        time_series_data.append(TimeSeriesDataPoint(
            date=metric.metric_date,
            floor_price_usd=metric.floor_price_usd,
            volume=metric.unified_volume_usd,
            listings_count=metric.active_listings_count,
            sales_count=metric.boxes_sold_per_day,
            market_cap=metric.visible_market_cap_usd,
        ))
    
    return time_series_data


@router.get("/{box_id}/sparkline", response_model=List[SparklineDataPoint])
async def get_sparkline(
    box_id: UUID,
    days: int = Query(default=7, ge=1, le=30, description="Number of days"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get sparkline price data for a booster box
    
    Returns price points for the last N days for sparkline chart visualization.
    """
    # Verify box exists
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Get sparkline data
    sparkline_list = await UnifiedMetricsRepository.get_sparkline_data(
        db, box_id, days
    )
    
    sparkline_data = [
        SparklineDataPoint(
            timestamp=sp["timestamp"],
            price=sp["price"]
        )
        for sp in sparkline_list
    ]
    
    return sparkline_data

