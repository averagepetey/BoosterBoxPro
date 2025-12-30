"""
Public Booster Boxes Router
Public API endpoints for leaderboard, box details, and analytics
"""

from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Optional, List
import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import BoxNotFoundError, MetricsNotFoundError, InvalidDateError
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
from app.dependencies.auth import get_current_user_required  # Phase 8: Authentication required
from app.services.cache_service import get_cache_service

router = APIRouter(prefix="/booster-boxes", tags=["booster-boxes"])

cache_service = get_cache_service()

cache_service = get_cache_service()


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
        units_sold_count=int(metrics.boxes_sold_per_day) if metrics.boxes_sold_per_day is not None else None,
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
    current_user = Depends(get_current_user_required),  # Phase 8: Authentication required
):
    """
    Get leaderboard of booster boxes
    
    Returns ranked list of booster boxes sorted by the specified field.
    Default sort is by 7-day EMA volume (highest first).
    """
    # Check if this is a cacheable query
    # Allow caching for default queries (no date = latest date) if other conditions met
    use_cache = (
        sort == "unified_volume_7d_ema" and 
        offset == 0 and 
        limit in [10, 50]
    )
    
    # If no date specified, use today's date for cache key
    cache_date = date_param if date_param else date.today()
    
    # Try cache first (cache stores full formatted response + total count)
    if use_cache:
        try:
            cached_response = await cache_service.get_cached_leaderboard(cache_date, limit)
            if cached_response:
                # Cache hit - return immediately (no DB queries!)
                if isinstance(cached_response, dict) and 'data' in cached_response:
                    # Full cached response with total
                    return LeaderboardResponse(
                        data=[LeaderboardBoxResponse.model_validate(item) for item in cached_response['data']],
                        meta=ResponseMeta(
                            total=cached_response.get('total', len(cached_response['data'])),
                            sort=sort,
                            sort_direction="desc",
                            date=date_param,
                            limit=limit,
                            offset=offset
                        )
                    )
        except Exception as e:
            # If cache deserialization fails, fall through to DB query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache deserialization failed for leaderboard: {e}")
    
    # Cache miss - query database
    leaderboard_service = LeaderboardService(db)
    ranked_results = await leaderboard_service.get_ranked_boxes(
        target_date=date_param,
        sort_by=sort,
        sort_direction="desc",
        limit=limit,
        offset=offset
    )
    
    # Format response
    leaderboard_boxes = []
    for box, metrics, rank, rank_change_info in ranked_results:
        leaderboard_box = format_leaderboard_box(box, metrics, rank, rank_change_info)
        leaderboard_boxes.append(leaderboard_box)
    
    # Get total count (optimized: use count query instead of fetching all records)
    if date_param:
        from sqlalchemy import func, select
        from app.models.unified_box_metrics import UnifiedBoxMetrics
        result = await db.execute(
            select(func.count(UnifiedBoxMetrics.id))
            .where(UnifiedBoxMetrics.metric_date == date_param)
        )
        total = result.scalar() or 0
    else:
        # For latest, we need to count distinct boxes (more complex)
        all_metrics = await UnifiedMetricsRepository.get_latest_for_all_boxes(db, None)
        total = len(all_metrics)
    
    # Cache formatted response for future requests (include total count)
    if use_cache and leaderboard_boxes:
        cache_formatted_data = {
            'data': [box.model_dump() for box in leaderboard_boxes],
            'total': total
        }
        await cache_service.cache_leaderboard(cache_date, limit, cache_formatted_data)
    
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
    current_user = Depends(get_current_user_required),  # Phase 8: Authentication required
):
    """
    Get detailed analytics for a specific booster box
    
    Returns comprehensive metrics, time-series data, and advanced analytics.
    This is the endpoint for the detail page accessed by clicking a box from the leaderboard.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Use today's date as default for caching
    cache_date = date_param or date.today()
    
    # Try cache first - check both cache_date and today's date for flexibility
    try:
        # First try with requested cache_date
        cached_json = await cache_service.get_cached_box_detail(box_id, cache_date)
        
        # If not found and no date_param specified, also try today's date
        if not cached_json and not date_param:
            today_date = date.today()
            if today_date != cache_date:
                cached_json = await cache_service.get_cached_box_detail(box_id, today_date)
        
        if cached_json:
            # Cache hit - return JSON string directly (fastest path!)
            # This completely bypasses Pydantic validation and serialization overhead
            from fastapi import Response
            return Response(
                content=cached_json,
                media_type="application/json",
                headers={"X-Cache": "HIT"}
            )
    except Exception as e:
        # If cache retrieval fails, fall through to DB query
        logger.warning(f"Cache retrieval failed for box {box_id}: {e}")
    
    try:
        # Cache miss - query database
        # Get box
        box = await BoosterBoxRepository.get_by_id(db, box_id)
        if not box:
            raise BoxNotFoundError(f"Booster box with id {box_id} not found")
        
        # Get metrics for specified date or latest
        if date_param:
            metrics = await UnifiedMetricsRepository.get_by_box_and_date(db, box_id, date_param)
        else:
            metrics = await UnifiedMetricsRepository.get_latest_for_box(db, box_id)
        
        if not metrics:
            raise MetricsNotFoundError(f"Metrics not found for box {box_id} on date {date_param or 'latest'}")
        
        # Update cache_date to match actual metrics date for consistency
        # This ensures cache hits when querying without a date parameter
        cache_date = metrics.metric_date if not date_param else cache_date
        
        # Get rank (use rank from metrics if available, otherwise calculate)
        rank = metrics.current_rank
        if rank is None:
            try:
                leaderboard_service = LeaderboardService(db)
                rank = await leaderboard_service.get_box_rank(box_id, metrics.metric_date)
                if rank is None:
                    rank = 9999  # Placeholder for unranked boxes
            except Exception as e:
                logger.warning(f"Failed to calculate rank for box {box_id}: {e}")
                rank = 9999  # Placeholder for unranked boxes
        
        # Get rank change info from metrics (stored rank_change field)
        rank_change_info = None
        if metrics.rank_change is not None:
            if metrics.rank_change > 0:
                direction = "up"
            elif metrics.rank_change < 0:
                direction = "down"
            else:
                direction = "same"
            rank_change_info = {
                "direction": direction,
                "amount": abs(metrics.rank_change)
            }
        
        # Get time-series data and rank history in parallel (optimization)
        end_date = metrics.metric_date
        start_date = end_date - timedelta(days=30)
        
        # Fetch both in parallel if possible (for async optimization)
        time_series_metrics_task = UnifiedMetricsRepository.get_by_box_date_range(
            db, box_id, start_date, end_date
        )
        rank_history_task = UnifiedMetricsRepository.get_rank_history(
            db, box_id, start_date, end_date
        )
        
        # Execute both queries
        time_series_metrics, rank_history_list = await asyncio.gather(
            time_series_metrics_task,
            rank_history_task,
            return_exceptions=True
        )
        
        # Process time-series data
        if isinstance(time_series_metrics, Exception):
            logger.warning(f"Failed to get time-series for box {box_id}: {time_series_metrics}")
            time_series_data = []
        else:
            time_series_data = []
            for ts_metric in time_series_metrics:
                time_series_data.append(TimeSeriesDataPoint(
                    date=ts_metric.metric_date,
                    floor_price_usd=ts_metric.floor_price_usd,
                    volume=ts_metric.unified_volume_usd,
                    listings_count=ts_metric.active_listings_count,
                    sales_count=int(ts_metric.boxes_sold_per_day) if ts_metric.boxes_sold_per_day is not None else None,
                    market_cap=ts_metric.visible_market_cap_usd,
                ))
        
        # Process rank history - handle None ranks gracefully
        if isinstance(rank_history_list, Exception):
            logger.warning(f"Failed to get rank history for box {box_id}: {rank_history_list}")
            rank_history = []
        else:
            rank_history = []
            for rh in rank_history_list:
                try:
                    # Handle date conversion
                    rank_date = rh.get("date")
                    if rank_date is None:
                        continue
                    if not isinstance(rank_date, date):
                        if isinstance(rank_date, str):
                            rank_date = date.fromisoformat(rank_date)
                        else:
                            continue  # Skip invalid dates
                    
                    # Handle rank (must be an int, not None)
                    rank_value = rh.get("rank")
                    if rank_value is None:
                        continue  # Skip entries without rank
                    
                    rank_history.append(RankHistoryPoint(
                        date=rank_date,
                        rank=int(rank_value),
                        rank_change=rh.get("rank_change")
                    ))
                except (ValueError, KeyError, TypeError) as e:
                    # Skip invalid entries
                    logger.warning(f"Skipping invalid rank history entry: {rh}, error: {e}")
                    continue
        
        # Build detailed metrics
        detail_metrics = BoxDetailMetrics(
            floor_price_usd=metrics.floor_price_usd,
            floor_price_1d_change_pct=metrics.floor_price_1d_change_pct,
            daily_volume_usd=metrics.unified_volume_usd,
            unified_volume_7d_ema=metrics.unified_volume_7d_ema,
            unified_volume_30d_sma=metrics.unified_volume_30d_sma,
            units_sold_count=int(metrics.boxes_sold_per_day) if metrics.boxes_sold_per_day is not None else None,
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
        
        response = BoxDetailResponse(
            id=box.id,
            product_name=box.product_name,
            set_name=box.set_name,
            game_type=box.game_type,
            image_url=box.image_url,
            release_date=box.release_date,
            reprint_risk=box.reprint_risk or "LOW",  # Ensure it's never None
            estimated_total_supply=box.estimated_total_supply,
            rank=rank,
            rank_change_direction=rank_change_info.get("direction") if rank_change_info else None,
            rank_change_amount=rank_change_info.get("amount") if rank_change_info else None,
            metrics=detail_metrics,
            metric_date=metrics.metric_date,
            time_series_data=time_series_data if time_series_data else [],
            rank_history=rank_history if rank_history else [],
        )
        
        # Cache the response (use mode='json' for better JSON serialization of nested models)
        # Cache with the cache_date to match what we check for on retrieval
        try:
            await cache_service.cache_box_detail(box_id, cache_date, response.model_dump(mode='json'))
        except Exception as e:
            logger.warning(f"Failed to cache box detail for {box_id}: {e}")
        
        return response
    except (BoxNotFoundError, MetricsNotFoundError):
        raise  # Re-raise our custom errors
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Unexpected error in box detail endpoint for {box_id}: {e}", exc_info=True)
        raise  # Re-raise to trigger error handler


@router.get("/{box_id}/time-series", response_model=List[TimeSeriesDataPoint])
async def get_time_series(
    box_id: UUID,
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_required),  # Phase 8: Authentication required
):
    """
    Get time-series data for a booster box
    
    Returns historical daily metrics over a date range.
    """
    # Default to last 30 days if not specified
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Try cache first (for common 30-day queries)
    use_cache = (
        (end_date - start_date).days == 30 and
        end_date == date.today()
    )
    
    if use_cache:
        try:
            cached_data = await cache_service.get_cached_time_series(box_id, start_date, end_date)
            if cached_data:
                # Cache hit - return immediately
                return [TimeSeriesDataPoint.model_validate(item) for item in cached_data]
        except Exception as e:
            # If cache deserialization fails, fall through to DB query
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache deserialization failed for time-series: {e}")
    
    # Cache miss or not cacheable - verify box exists and query database
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise BoxNotFoundError(f"Booster box with id {box_id} not found")
    
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
            sales_count=int(metric.boxes_sold_per_day) if metric.boxes_sold_per_day is not None else None,
            market_cap=metric.visible_market_cap_usd,
        ))
    
    # Cache the response
    if use_cache and time_series_data:
        cache_formatted_data = [item.model_dump() for item in time_series_data]
        await cache_service.cache_time_series(box_id, start_date, end_date, cache_formatted_data)
    
    return time_series_data


@router.get("/{box_id}/sparkline", response_model=List[SparklineDataPoint])
async def get_sparkline(
    box_id: UUID,
    days: int = Query(default=7, ge=1, le=30, description="Number of days"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_required),  # Phase 8: Authentication required
):
    """
    Get sparkline price data for a booster box
    
    Returns price points for the last N days for sparkline chart visualization.
    """
    # Verify box exists
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise BoxNotFoundError(f"Booster box with id {box_id} not found")
    
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

