"""
Volume Calculation Service
Handles volume calculations for booster boxes with support for:
- Current: Sparse historical data (entries at various intervals)
- Future: Daily snapshots (will enable more accurate calculations)

When daily snapshots are available, this module will be updated to:
1. Sum actual daily volumes instead of extrapolating
2. Use true rolling 30-day windows
3. Calculate actual price distributions from daily data
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


def calculate_volume_from_sparse_data(
    floor_price: float,
    boxes_sold_per_day: float,
    active_listings: Optional[int] = None,
    price_change_pct: Optional[float] = None,
    days: int = 30
) -> float:
    """
    Calculate volume from sparse historical data.
    
    CURRENT IMPLEMENTATION: Uses market efficiency factor with adjustments
    FUTURE: When daily snapshots are available, use calculate_volume_from_daily_snapshots()
    
    Args:
        floor_price: Current floor price
        boxes_sold_per_day: Average boxes sold per day
        active_listings: Number of active listings (for liquidity adjustment)
        price_change_pct: Price change percentage (for trend adjustment)
        days: Number of days to calculate volume for (default 30)
    
    Returns:
        Calculated volume in USD
    """
    if not floor_price or not boxes_sold_per_day or boxes_sold_per_day <= 0:
        return 0.0
    
    # Base market efficiency factor: 92% of floor price
    # Accounts for: private sales, quick sales, some above floor
    base_factor = 0.92
    
    # Liquidity adjustment
    liquidity_adjustment = 0.0
    if active_listings is not None:
        if active_listings > 20:
            liquidity_adjustment = -0.02  # High liquidity: 2% lower average
        elif active_listings > 10:
            liquidity_adjustment = -0.01  # Medium liquidity: 1% lower
        else:
            liquidity_adjustment = 0.01   # Low liquidity: 1% higher (closer to floor)
    
    # Price trend adjustment
    trend_adjustment = 0.0
    if price_change_pct is not None:
        if price_change_pct > 5:
            trend_adjustment = 0.03  # Rising prices: sales likely higher
        elif price_change_pct < -5:
            trend_adjustment = -0.05  # Falling prices: sales likely lower
    
    # Calculate adjusted average sale price
    adjusted_factor = base_factor + liquidity_adjustment + trend_adjustment
    adjusted_factor = max(0.85, min(0.98, adjusted_factor))  # Clamp between 85% and 98%
    
    average_sale_price = floor_price * adjusted_factor
    daily_volume = average_sale_price * boxes_sold_per_day
    
    return daily_volume * days


def calculate_volume_from_daily_snapshots(
    daily_snapshots: List[Dict[str, Any]],
    days: int = 30
) -> float:
    """
    Calculate volume from daily snapshots (FUTURE IMPLEMENTATION).
    
    This will be used when daily snapshots are available.
    It sums actual daily volumes instead of extrapolating.
    
    Args:
        daily_snapshots: List of daily snapshot data with:
            - date: Date of snapshot
            - floor_price_usd: Floor price on that day
            - boxes_sold_per_day: Boxes sold on that day
            - active_listings_count: Active listings on that day
            - (future: actual_sale_prices distribution)
        days: Number of days to include (default 30, for rolling window)
    
    Returns:
        Calculated volume in USD
    """
    # TODO: Implement when daily snapshots are available
    # This will:
    # 1. Filter snapshots to last N days
    # 2. For each day, calculate volume using that day's data
    # 3. Sum all daily volumes
    # 4. Optionally use actual sale price distributions if available
    
    if not daily_snapshots:
        return 0.0
    
    # Sort by date
    sorted_snapshots = sorted(daily_snapshots, key=lambda x: x.get('date', ''))
    
    # Get last N days
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent_snapshots = [s for s in sorted_snapshots if s.get('date', '') >= cutoff_date]
    
    total_volume = 0.0
    for snapshot in recent_snapshots:
        floor_price = snapshot.get('floor_price_usd', 0)
        boxes_sold = snapshot.get('boxes_sold_per_day', 0) or 0
        active_listings = snapshot.get('active_listings_count', 0) or 0
        
        if floor_price > 0 and boxes_sold > 0:
            # Use same calculation as sparse data for now
            # When actual sale prices are available, use those instead
            daily_volume = calculate_volume_from_sparse_data(
                floor_price=floor_price,
                boxes_sold_per_day=boxes_sold,
                active_listings=active_listings,
                days=1  # Calculate for single day
            )
            total_volume += daily_volume
    
    return total_volume


def calculate_rolling_30d_volume_ema(
    daily_volumes: List[float],
    period: int = 7
) -> float:
    """
    Calculate exponential moving average of 30-day volumes.
    
    FUTURE: Will use actual daily volumes when snapshots are available.
    CURRENT: Uses calculated volumes from sparse data points.
    
    Args:
        daily_volumes: List of 30-day volumes (one per data point)
        period: EMA period (default 7 days)
    
    Returns:
        EMA of volumes
    """
    if not daily_volumes:
        return 0.0
    
    if len(daily_volumes) == 1:
        return daily_volumes[0]
    
    # Calculate EMA
    alpha = 2 / (period + 1)
    ema = daily_volumes[0]
    
    for volume in daily_volumes[1:]:
        ema = (volume * alpha) + (ema * (1 - alpha))
    
    return ema




