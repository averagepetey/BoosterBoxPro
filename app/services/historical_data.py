"""
Historical Data Service
Handles loading and processing historical data for boxes
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

# In-memory cache for load_historical_entries to avoid re-reading JSON on every box
# (leaderboard calls get_box_historical_data 4+ times per box; this cuts file reads to 1 per minute)
_historical_entries_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None
_historical_entries_cache_time: float = 0
_HISTORICAL_CACHE_TTL_SECONDS: float = 60.0


def load_historical_entries() -> Dict[str, List[Dict[str, Any]]]:
    """Load all historical entries from JSON file (cached 60s to speed up leaderboard)."""
    global _historical_entries_cache, _historical_entries_cache_time
    now = time.monotonic()
    if _historical_entries_cache is not None and (now - _historical_entries_cache_time) < _HISTORICAL_CACHE_TTL_SECONDS:
        return _historical_entries_cache
    historical_file = Path(__file__).parent.parent.parent / "data" / "historical_entries.json"
    if not historical_file.exists():
        _historical_entries_cache = {}
        _historical_entries_cache_time = now
        return _historical_entries_cache
    with open(historical_file, 'r') as f:
        _historical_entries_cache = json.load(f)
    _historical_entries_cache_time = now
    return _historical_entries_cache


# Mapping of database UUIDs to old leaderboard UUIDs
# This allows merging historical data that was saved under different IDs
DB_TO_LEADERBOARD_UUID_MAP = {
    # Blue/White variants
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": "550e8400-e29b-41d4-a716-446655440001",  # OP-01 Blue
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": "550e8400-e29b-41d4-a716-446655440002",  # OP-01 White
    # Main sets
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": "550e8400-e29b-41d4-a716-446655440003",  # OP-02
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": "550e8400-e29b-41d4-a716-446655440004",  # OP-03
    "526c28b7-bc13-449b-a521-e63bdd81811a": "550e8400-e29b-41d4-a716-446655440005",  # OP-04
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": "550e8400-e29b-41d4-a716-446655440006",  # OP-05
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": "550e8400-e29b-41d4-a716-446655440007",  # OP-06
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": "550e8400-e29b-41d4-a716-446655440009",  # OP-07
    "d0faf871-a930-4c80-a981-9df8741c90a9": "550e8400-e29b-41d4-a716-446655440010",  # OP-08
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": "550e8400-e29b-41d4-a716-446655440012",  # OP-09
    "3429708c-43c3-4ed8-8be3-706db8b062bd": "550e8400-e29b-41d4-a716-446655440013",  # OP-10
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": "550e8400-e29b-41d4-a716-446655440015",  # OP-11
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": "550e8400-e29b-41d4-a716-446655440016",  # OP-12
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": "550e8400-e29b-41d4-a716-446655440018",  # OP-13
    # Extra boosters
    "3b17b708-b35b-4008-971e-240ade7afc9c": "550e8400-e29b-41d4-a716-446655440008",  # EB-01
    "7509a855-f6da-445e-b445-130824d81d04": "550e8400-e29b-41d4-a716-446655440014",  # EB-02
    # Premium boosters
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": "550e8400-e29b-41d4-a716-446655440011",  # PRB-01
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": "550e8400-e29b-41d4-a716-446655440017",  # PRB-02
}

# Reverse mapping
LEADERBOARD_TO_DB_UUID_MAP = {v: k for k, v in DB_TO_LEADERBOARD_UUID_MAP.items()}


def merge_same_date_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge multiple entries for the same date into a single consolidated entry.
    Sums up sales data and takes the best available values for other metrics.
    """
    # Group entries by date
    by_date = defaultdict(list)
    for entry in entries:
        date_str = entry.get('date', '')
        if date_str:
            by_date[date_str].append(entry)
    
    # Merge entries for each date
    merged = []
    for date_str in sorted(by_date.keys()):
        date_entries = by_date[date_str]
        
        if len(date_entries) == 1:
            merged.append(date_entries[0])
            continue
        
        # Merge multiple entries for the same date
        base = date_entries[0].copy()
        
        # Sum up sales data
        total_boxes_sold = 0
        total_listings = 0
        all_sales = []
        all_listings = []
        
        for entry in date_entries:
            # Collect raw sales and listings
            if entry.get('raw_sales'):
                all_sales.extend(entry.get('raw_sales', []))
            if entry.get('raw_listings'):
                all_listings.extend(entry.get('raw_listings', []))
            
            # Sum boxes sold from the field (as fallback)
            boxes_sold = entry.get('boxes_sold_today') or entry.get('boxes_sold_per_day') or 0
            total_boxes_sold += boxes_sold
            
            # Take the max listings count
            entry_listings = entry.get('active_listings_count') or 0
            if entry_listings > total_listings:
                total_listings = entry_listings
            
            # Take the floor price from entry with listings (current market price)
            # If no listings, use the lowest price available
            entry_listings_count = entry.get('active_listings_count', 0) or 0
            entry_has_listings = entry_listings_count > 0 or entry.get('raw_listings')
            
            if entry.get('floor_price_usd') and entry['floor_price_usd'] > 0:
                if entry_has_listings:
                    # Prioritize floor price from entries with listings (current market)
                    base['floor_price_usd'] = entry['floor_price_usd']
                elif not base.get('floor_price_usd') or entry['floor_price_usd'] < base['floor_price_usd']:
                    # If no listings in any entry, use lowest price
                    base['floor_price_usd'] = entry['floor_price_usd']
            
            # Take the best unified_volume_7d_ema if available
            if entry.get('unified_volume_7d_ema') and entry['unified_volume_7d_ema'] > 0:
                base['unified_volume_7d_ema'] = entry['unified_volume_7d_ema']
        
        # Count actual sales from raw_sales if available (more accurate than boxes_sold fields)
        if all_sales:
            # Count unique sales (sum quantities)
            actual_sales_count = sum(s.get('quantity', 1) for s in all_sales)
            total_boxes_sold = actual_sales_count
        
        # Count listings added from raw_listings if available
        # This counts the number of listings, not total quantity of boxes
        total_listings_added = 0
        if all_listings:
            total_listings_added = len(all_listings)
        else:
            # Fallback to summing boxes_added_today fields
            for entry in date_entries:
                total_listings_added += entry.get('boxes_added_today', 0) or 0
        
        # Count active listings within 20% of floor price
        floor_price = base.get('floor_price_usd')
        if floor_price and floor_price > 0 and all_listings:
            max_price = floor_price * 1.20  # 20% above floor
            listings_within_20pct = [
                l for l in all_listings
                if (l.get('price', 0) or 0) + (l.get('shipping', 0) or 0) <= max_price
            ]
            total_listings = len(listings_within_20pct)
        elif floor_price and floor_price > 0:
            # If we have floor price but no raw_listings, filter by active_listings_count
            # (assuming it was already filtered during processing)
            total_listings = total_listings  # Keep existing count
        # else: total_listings stays as max from entries
        
        # Update merged entry
        base['boxes_sold_today'] = total_boxes_sold
        base['boxes_sold_per_day'] = total_boxes_sold
        base['boxes_added_today'] = total_listings_added
        base['active_listings_count'] = total_listings
        if all_sales:
            base['raw_sales'] = all_sales
        if all_listings:
            base['raw_listings'] = all_listings
        
        merged.append(base)
    
    return merged


def get_box_historical_data(box_id: str, prefer_db: bool = True) -> List[Dict[str, Any]]:
    """
    Get historical data for a specific box.
    When prefer_db=True (default), reads from box_metrics_unified first; falls back to
    historical_entries.json so behavior and calculations stay the same.
    Merges data from both database UUID and old leaderboard UUID when using JSON.
    """
    # Prefer DB: same entry shape, no formula changes
    if prefer_db:
        try:
            from app.services.db_historical_reader import get_box_historical_entries_from_db
            resolved_id = LEADERBOARD_TO_DB_UUID_MAP.get(box_id, box_id)
            db_entries = get_box_historical_entries_from_db(resolved_id)
            if db_entries:
                entries = merge_same_date_entries(db_entries)
                entries.sort(key=lambda x: x.get('date', ''))
                return entries
        except Exception:
            pass
    # Fallback: JSON (unchanged behavior)
    historical_data = load_historical_entries()
    entries = list(historical_data.get(box_id, []))
    alternate_id = None
    if box_id in DB_TO_LEADERBOARD_UUID_MAP:
        alternate_id = DB_TO_LEADERBOARD_UUID_MAP[box_id]
    elif box_id in LEADERBOARD_TO_DB_UUID_MAP:
        alternate_id = LEADERBOARD_TO_DB_UUID_MAP[box_id]
    if alternate_id and alternate_id in historical_data:
        entries.extend(historical_data[alternate_id])
    entries = merge_same_date_entries(entries)
    entries.sort(key=lambda x: x.get('date', ''))
    return entries


def filter_to_one_per_month(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter data to one entry per month (uses the last entry of each month, with averaged daily sales)"""
    from collections import defaultdict
    
    # Group entries by month
    by_month = defaultdict(list)
    for entry in data:
        date_str = entry.get('date')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                by_month[month_key].append(entry)
            except (ValueError, TypeError):
                continue
    
    # Get the last entry from each month and calculate average daily sales for that month
    result = []
    for month in sorted(by_month.keys()):
        entries = by_month[month]
        # Sort by date and take the last one as the base entry
        entries.sort(key=lambda x: x.get('date', ''))
        base_entry = entries[-1].copy()
        
        # Calculate average boxes_sold_per_day for all entries in this month
        daily_sales_values = [e.get('boxes_sold_per_day', 0) or 0 for e in entries if e.get('boxes_sold_per_day', 0) or 0 > 0]
        if daily_sales_values:
            avg_daily_sales = sum(daily_sales_values) / len(daily_sales_values)
            base_entry['boxes_sold_per_day'] = round(avg_daily_sales, 2)
        # If all are 0, keep 0
        
        result.append(base_entry)
    
    # Re-sort by date to maintain chronological order
    result.sort(key=lambda x: x.get('date', ''))
    return result


def get_box_price_history(box_id: str, days: Optional[int] = None, one_per_month: bool = False) -> List[Dict[str, Any]]:
    """Get price history for a box, optionally limited to last N days"""
    entries = get_box_historical_data(box_id)
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    # Filter by days if specified
    # If days is 365 or more, return all data (no filtering)
    if days and days < 365:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        entries = [e for e in entries if e.get('date', '') >= cutoff_date]
    
    # Format for time-series chart and calculate derived metrics
    result = []
    for i, entry in enumerate(entries):
        if entry.get('floor_price_usd') is None:
            continue
        
        floor_price = entry.get('floor_price_usd', 0)
        
        # Recalculate boxes_sold_per_day from raw_sales if available (more accurate)
        boxes_sold_per_day = entry.get('boxes_sold_per_day', 0) or 0
        if entry.get('raw_sales'):
            # Count actual boxes sold from raw_sales
            total_sold = sum(s.get('quantity', 1) for s in entry.get('raw_sales', []))
            if total_sold > 0:
                boxes_sold_per_day = total_sold
        
        # Calculate 1-day change percentage
        floor_price_1d_change_pct = None
        if i > 0:
            prev_entry = entries[i - 1]
            prev_price = prev_entry.get('floor_price_usd')
            if prev_price and prev_price > 0:
                floor_price_1d_change_pct = ((floor_price - prev_price) / prev_price) * 100
        
        # Calculate units sold based on daily average and days between entries
        units_sold_count = None
        days_between = None
        if i > 0:
            # Get previous entry date
            prev_entry = entries[i - 1]
            prev_date_str = prev_entry.get('date')
            current_date_str = entry.get('date')
            
            if prev_date_str and current_date_str:
                try:
                    prev_date = datetime.strptime(prev_date_str, '%Y-%m-%d')
                    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
                    
                    # Calculate days between entries
                    days_between = (current_date - prev_date).days
                    
                    if days_between > 0:
                        # boxes_sold_per_day is already a daily average (one day's worth of sales)
                        # Use the current period's daily rate multiplied by days between entries
                        if boxes_sold_per_day > 0:
                            # Use current period's daily rate
                            units_sold_count = round(boxes_sold_per_day * days_between, 1)
                        else:
                            # If current period is 0, use previous period's rate
                            prev_boxes_sold_per_day = prev_entry.get('boxes_sold_per_day', 0) or 0
                            if prev_boxes_sold_per_day > 0:
                                units_sold_count = round(prev_boxes_sold_per_day * days_between, 1)
                except (ValueError, TypeError):
                    pass  # Skip calculation if date parsing fails
        
        # Calculate volume accurately
        # Volume should represent 30-day volume
        # Account for fact that not all boxes sell at floor price
        # 
        # CURRENT STATE: Sparse historical data (entries at various intervals)
        # FUTURE STATE: Daily snapshots will provide more accurate calculations
        #
        # Strategy: Use market efficiency factor with adjustments based on available data
        # When daily snapshots are available, we can calculate true rolling averages
        unified_volume_usd = None
        daily_volume_usd = None
        if floor_price and boxes_sold_per_day:
            # Market efficiency factor: accounts for sales above and below floor
            # Base factor: 92% of floor price (accounts for private sales, quick sales, etc.)
            market_efficiency_factor = 0.92
            
            # Adjust factor based on available market signals
            # When we have daily snapshots, we can use actual price distributions
            active_listings = entry.get('active_listings_count', 0) or 0
            
            # More listings = more competition = slightly lower average price
            # Less listings = less competition = closer to floor price
            if active_listings > 20:
                liquidity_adjustment = -0.02  # High liquidity: 2% lower
            elif active_listings > 10:
                liquidity_adjustment = -0.01  # Medium liquidity: 1% lower
            else:
                liquidity_adjustment = 0.01   # Low liquidity: 1% higher (closer to floor)
            
            # Adjust for price trend if available
            price_trend_adjustment = 0
            if floor_price_1d_change_pct is not None:
                if floor_price_1d_change_pct > 5:
                    price_trend_adjustment = 0.03  # Rising prices: sales likely higher
                elif floor_price_1d_change_pct < -5:
                    price_trend_adjustment = -0.05  # Falling prices: sales likely lower
            
            # Calculate adjusted average sale price
            adjusted_factor = market_efficiency_factor + liquidity_adjustment + price_trend_adjustment
            adjusted_factor = max(0.85, min(0.98, adjusted_factor))  # Clamp between 85% and 98%
            average_sale_price = floor_price * adjusted_factor
            
            # Calculate daily volume - prefer stored data, then raw sales, then estimate
            daily_volume_usd = None
            
            # Priority 1: Use stored daily_volume_usd if available (from screenshot capture)
            if entry.get('daily_volume_usd') and entry.get('daily_volume_usd') > 0:
                daily_volume_usd = entry.get('daily_volume_usd')
            # Priority 2: Use actual raw sales data if available
            elif entry.get('raw_sales'):
                raw_sales = entry.get('raw_sales', [])
                daily_volume_usd = sum((s.get('price', 0) + s.get('shipping', 0)) * s.get('quantity', 1) for s in raw_sales)
            # Priority 3: Estimate daily volume using average sale price
            else:
                daily_volume_usd = average_sale_price * boxes_sold_per_day
            
            # For 30-day volume: prefer stored value, otherwise calculate from daily
            # NOTE: When daily snapshots are available, we'll sum actual daily volumes
            if entry.get('unified_volume_usd') and entry.get('unified_volume_usd') > 0:
                unified_volume_usd = entry.get('unified_volume_usd')
            else:
                unified_volume_usd = daily_volume_usd * 30 if daily_volume_usd else None
        elif floor_price and units_sold_count and units_sold_count > 0:
            # Fallback: if we have units_sold_count but no daily rate, estimate daily
            # This handles cases where boxes_sold_per_day might be missing
            if days_between and days_between > 0:
                estimated_daily = units_sold_count / days_between
                market_efficiency_factor = 0.92
                average_sale_price = floor_price * market_efficiency_factor
                daily_volume_usd = average_sale_price * estimated_daily
                unified_volume_usd = daily_volume_usd * 30
        
        # Ensure date is in correct format (YYYY-MM-DD)
        date_str = entry.get('date')
        if date_str:
            # Parse and reformat to ensure consistency
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                pass  # Keep original if parsing fails
        
        # Calculate 7-day EMA of daily volume
        # All volume metrics must be calculated from daily_volume_usd, not estimates
        unified_volume_7d_ema = None
        if daily_volume_usd:
            if i == 0:
                # First entry: use current daily volume as initial EMA
                unified_volume_7d_ema = daily_volume_usd
            else:
                # Get previous EMA from result (this accumulates across entries)
                prev_ema = result[-1].get('unified_volume_7d_ema') if result else None
                
                if prev_ema:
                    # Calculate EMA with smoothing factor for 7-day period
                    # Alpha = 2/(N+1) where N=7 for 7-day EMA
                    alpha = 2 / (7 + 1)  # Smoothing factor = 0.25
                    calculated_ema = (daily_volume_usd * alpha) + (prev_ema * (1 - alpha))
                    # Ensure EMA is at least equal to current daily volume
                    # This ensures the metric reflects current activity level
                    unified_volume_7d_ema = max(calculated_ema, daily_volume_usd)
                else:
                    # Fallback: use current daily volume
                    unified_volume_7d_ema = daily_volume_usd
        elif unified_volume_usd:
            # Fallback: if no daily volume, derive from 30-day estimate
            # This should rarely happen if we have proper daily data
            daily_proxy = unified_volume_usd / 30 if unified_volume_usd else None
            if daily_proxy:
                if i == 0:
                    unified_volume_7d_ema = daily_proxy
                else:
                    prev_ema = result[-1].get('unified_volume_7d_ema') if result else None
                    if prev_ema:
                        alpha = 2 / (7 + 1)
                        unified_volume_7d_ema = (daily_proxy * alpha) + (prev_ema * (1 - alpha))
                    else:
                        unified_volume_7d_ema = daily_proxy
        
        result.append({
            'date': date_str,
            'floor_price_usd': floor_price,
            'floor_price_1d_change_pct': floor_price_1d_change_pct,
            'active_listings_count': entry.get('active_listings_count'),
            'boxes_sold_per_day': boxes_sold_per_day,
            'boxes_added_today': entry.get('boxes_added_today'),
            'daily_volume_usd': daily_volume_usd,
            'unified_volume_usd': unified_volume_usd,
            'unified_volume_7d_ema': unified_volume_7d_ema,
            'units_sold_count': units_sold_count,
            'days_to_20pct_increase': None,  # Would need calculation
        })
    
    # Filter to one entry per month if requested
    if one_per_month:
        result = filter_to_one_per_month(result)
        # Recalculate metrics after filtering for monthly data
        import calendar
        for i in range(len(result)):
            entry = result[i]
            date_str = entry.get('date')
            
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    year = date_obj.year
                    month = date_obj.month
                    
                    # Calculate days in that month
                    days_in_month = calendar.monthrange(year, month)[1]
                    
                    # Recalculate units sold: daily average * days in month
                    boxes_sold_per_day = entry.get('boxes_sold_per_day', 0) or 0
                    # Always recalculate, even if 0
                    units_sold_count = round(boxes_sold_per_day * days_in_month, 1)
                    result[i]['units_sold_count'] = units_sold_count
                    
                    # Recalculate volume: 30-day volume using market efficiency factor
                    # For monthly aggregated data, use the monthly average daily sales
                    floor_price = entry.get('floor_price_usd', 0)
                    if floor_price > 0 and boxes_sold_per_day > 0:
                        # Use market efficiency factor with adjustments
                        # When daily snapshots are available, we can calculate true monthly volume
                        # by summing daily volumes instead of using monthly average
                        market_efficiency_factor = 0.92
                        average_sale_price = floor_price * market_efficiency_factor
                        daily_volume = average_sale_price * boxes_sold_per_day
                        result[i]['unified_volume_usd'] = daily_volume * 30
                    elif floor_price > 0:
                        # If units_sold is 0, volume should also be 0
                        result[i]['unified_volume_usd'] = 0
                except (ValueError, TypeError):
                    pass  # Skip if date parsing fails
            
            # Recalculate change percentage (month-over-month)
            if i > 0:
                prev_entry = result[i - 1]
                current_entry = result[i]
                
                if prev_entry.get('floor_price_usd') and current_entry.get('floor_price_usd'):
                    prev_price = prev_entry['floor_price_usd']
                    curr_price = current_entry['floor_price_usd']
                    if prev_price > 0:
                        result[i]['floor_price_1d_change_pct'] = ((curr_price - prev_price) / prev_price) * 100
                
                # Recalculate EMA
                prev_ema = prev_entry.get('unified_volume_7d_ema')
                curr_volume = current_entry.get('unified_volume_usd')
                if prev_ema and curr_volume:
                    alpha = 2 / (7 + 1)
                    result[i]['unified_volume_7d_ema'] = (curr_volume * alpha) + (prev_ema * (1 - alpha))
    
    return result


def calculate_monthly_rankings() -> Dict[str, Dict[str, int]]:
    """
    Calculate rankings for each month based on historical floor prices.
    Returns: {date: {box_id: rank}}
    """
    historical_data = load_historical_entries()
    
    # Group entries by date
    entries_by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    for box_id, entries in historical_data.items():
        for entry in entries:
            date = entry.get('date')
            if date:
                entries_by_date[date].append({
                    'box_id': box_id,
                    'floor_price_usd': entry.get('floor_price_usd', 0),
                    'date': date,
                })
    
    # Calculate rankings for each date
    rankings_by_date: Dict[str, Dict[str, int]] = {}
    
    for date, entries in entries_by_date.items():
        # Sort by floor price (descending - higher price = better rank)
        sorted_entries = sorted(
            entries,
            key=lambda x: x.get('floor_price_usd', 0),
            reverse=True
        )
        
        # Assign ranks (1 = highest price)
        date_rankings = {}
        for rank, entry in enumerate(sorted_entries, start=1):
            date_rankings[entry['box_id']] = rank
        
        rankings_by_date[date] = date_rankings
    
    return rankings_by_date


def get_box_30d_avg_sales(box_id: str) -> Optional[float]:
    """
    Calculate the 30-day average boxes sold per day for a box.
    Uses screenshot data from database when available, falls back to JSON historical data.
    Returns the average of boxes_sold_per_day from entries in the last 30 days.
    Includes all values (including zeros) for a true 30-day average.
    
    NOTE: For screenshot data, averages are calculated during processing and stored
    in boxes_sold_30d_avg in the database. This function primarily serves as a
    fallback for JSON-based data or when database values aren't available.
    """
    # Use historical data (which may include database entries merged in)
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    # Get entries from last 30 days
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_entries = [e for e in entries if e.get('date', '') >= cutoff_date]
    
    if not recent_entries:
        return None
    
    # Get all boxes_sold_per_day values (including zeros) for true average
    # Prioritize boxes_sold_today if boxes_sold_per_day is not available
    daily_sales = []
    for e in recent_entries:
        sold = e.get('boxes_sold_per_day') or e.get('boxes_sold_today') or 0
        daily_sales.append(float(sold) if sold else 0.0)
    
    if not daily_sales:
        return 0.0
    
    # Calculate average of all values
    avg_sales = sum(daily_sales) / len(daily_sales)
    return round(avg_sales, 2)


def get_box_30d_volume(box_id: str) -> Optional[float]:
    """
    Calculate true 30-day volume by summing volumes from historical entries
    over the last 30 days. Uses actual data points instead of extrapolating.
    
    Returns the total volume in USD over the last 30 days.
    """
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    if not entries:
        return None
    
    # Get cutoff date (30 days ago)
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Filter entries from last 30 days, or use most recent entry if none in last 30 days
    recent_entries = [e for e in entries if e.get('date', '') >= cutoff_date]
    
    # If no entries in last 30 days, use the most recent entry and apply it to full 30 days
    if not recent_entries:
        most_recent = entries[-1] if entries else None
        if not most_recent:
            return None
        recent_entries = [most_recent]
        # We'll use this entry for the full 30-day period
    
    total_volume = 0.0
    cutoff_date_obj = datetime.strptime(cutoff_date, '%Y-%m-%d')
    today = datetime.now()
    
    # Calculate volume for each period between entries
    for i, entry in enumerate(recent_entries):
        floor_price = entry.get('floor_price_usd', 0)
        boxes_sold_per_day = entry.get('boxes_sold_per_day', 0) or 0
        active_listings = entry.get('active_listings_count', 0) or 0
        entry_date_str = entry.get('date', '')
        
        if not floor_price or not boxes_sold_per_day or not entry_date_str:
            continue
        
        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            continue
        
        # Calculate days this entry represents in the 30-day window
        if i < len(recent_entries) - 1:
            # Not the last entry: use days until next entry
            next_entry = recent_entries[i + 1]
            next_date_str = next_entry.get('date', '')
            try:
                next_date = datetime.strptime(next_date_str, '%Y-%m-%d')
                # Period starts at max(entry_date, cutoff_date) and ends at next_date
                period_start = max(entry_date, cutoff_date_obj)
                period_end = min(next_date, today)
                days_in_period = max(1, (period_end - period_start).days)
            except (ValueError, TypeError):
                days_in_period = 1
        else:
            # Last entry: covers from entry date (or cutoff) to today, up to 30 days total
            period_start = max(entry_date, cutoff_date_obj)
            period_end = min(today, cutoff_date_obj + timedelta(days=30))
            days_in_period = max(1, (period_end - period_start).days)
        
        # If this is the only entry and we need to cover full 30 days
        if len(recent_entries) == 1:
            # Use this entry's rate for the full 30-day period
            days_in_period = 30
        
        # Calculate market efficiency factor with adjustments
        market_efficiency_factor = 0.92
        
        # Liquidity adjustment
        if active_listings > 20:
            liquidity_adjustment = -0.02
        elif active_listings > 10:
            liquidity_adjustment = -0.01
        else:
            liquidity_adjustment = 0.01
        
        # Price trend (compare to previous entry if available)
        price_trend_adjustment = 0
        if i > 0:
            prev_entry = recent_entries[i - 1]
            prev_price = prev_entry.get('floor_price_usd', 0)
            if prev_price and prev_price > 0:
                price_change_pct = ((floor_price - prev_price) / prev_price) * 100
                if price_change_pct > 5:
                    price_trend_adjustment = 0.03
                elif price_change_pct < -5:
                    price_trend_adjustment = -0.05
        
        # Calculate average sale price
        adjusted_factor = market_efficiency_factor + liquidity_adjustment + price_trend_adjustment
        adjusted_factor = max(0.85, min(0.98, adjusted_factor))
        average_sale_price = floor_price * adjusted_factor
        
        # Calculate volume for this period
        period_volume = average_sale_price * boxes_sold_per_day * days_in_period
        total_volume += period_volume
    
    return round(total_volume, 2)


def get_box_latest_volume(box_id: str) -> Optional[float]:
    """
    Get the latest unified_volume_7d_ema for a box from historical data.
    Returns the most recent 7-day EMA volume value.
    
    NOTE: For true 30-day volume, use get_box_30d_volume() instead.
    """
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    if not entries:
        return None
    
    # Get the most recent entry's volume
    # We need to calculate it using get_box_price_history to get the proper EMA
    price_history = get_box_price_history(box_id, days=None, one_per_month=False)
    
    if not price_history:
        return None
    
    # Get the latest entry's unified_volume_7d_ema
    latest_entry = price_history[-1]
    return latest_entry.get('unified_volume_7d_ema')


def get_box_month_over_month_price_change(box_id: str) -> Optional[float]:
    """
    Calculate the month-over-month price change percentage for a box.
    Compares the most recent monthly entry to the previous monthly entry.
    Returns the percentage change as a float (e.g., 5.5 for +5.5%).
    """
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Get monthly filtered data (one entry per month)
    monthly_data = filter_to_one_per_month(entries)
    
    if len(monthly_data) < 2:
        return None
    
    # Get the last two monthly entries
    current_entry = monthly_data[-1]
    previous_entry = monthly_data[-2]
    
    current_price = current_entry.get('floor_price_usd')
    previous_price = previous_entry.get('floor_price_usd')
    
    if current_price is None or current_price <= 0:
        return None
    
    if previous_price is None or previous_price <= 0:
        return None
    
    # Calculate percentage change
    change_pct = ((current_price - previous_price) / previous_price) * 100
    return round(change_pct, 2)


def get_box_30d_price_change(box_id: str) -> Optional[float]:
    """
    Calculate the 30-day price change percentage for a box.
    Compares the most recent floor price to the floor price from 30 days ago.
    Returns the percentage change as a float (e.g., 5.5 for +5.5%).
    """
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    if not entries:
        return None
    
    # Get most recent entry
    current_entry = entries[-1]
    current_price = current_entry.get('floor_price_usd')
    
    if current_price is None or current_price <= 0:
        return None
    
    # Get entry from 30 days ago (or closest to it)
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Find the entry closest to 30 days ago
    past_entry = None
    for entry in reversed(entries[:-1]):  # Exclude the most recent entry
        entry_date = entry.get('date', '')
        if entry_date <= cutoff_date:
            past_entry = entry
            break
    
    # If no entry found before cutoff, use the oldest entry we have
    if not past_entry and len(entries) > 1:
        past_entry = entries[0]
    
    if not past_entry:
        return None
    
    past_price = past_entry.get('floor_price_usd')
    
    if past_price is None or past_price <= 0:
        return None
    
    # Calculate percentage change
    change_pct = ((current_price - past_price) / past_price) * 100
    return round(change_pct, 2)


def get_box_30d_price_change_absolute(box_id: str) -> Optional[float]:
    """
    Calculate the absolute dollar amount change in the 30-day period.
    Returns the dollar difference (current_price - past_price).
    """
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    if not entries:
        return None
    
    # Get most recent entry
    current_entry = entries[-1]
    current_price = current_entry.get('floor_price_usd')
    
    if current_price is None or current_price <= 0:
        return None
    
    # Get entry from 30 days ago (or closest to it)
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Find the entry closest to 30 days ago
    past_entry = None
    for entry in reversed(entries[:-1]):  # Exclude the most recent entry
        entry_date = entry.get('date', '')
        if entry_date <= cutoff_date:
            past_entry = entry
            break
    
    # If no entry found before cutoff, use the oldest entry we have
    if not past_entry and len(entries) > 1:
        past_entry = entries[0]
    
    if not past_entry:
        return None
    
    past_price = past_entry.get('floor_price_usd')
    
    if past_price is None or past_price <= 0:
        return None
    
    # Calculate absolute dollar change
    change_absolute = current_price - past_price
    return round(change_absolute, 2)


def get_box_rank_history(box_id: str, days: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get rank history for a box based on historical data"""
    monthly_rankings = calculate_monthly_rankings()
    
    # Get all dates this box has data for
    historical_data = load_historical_entries()
    box_entries = historical_data.get(box_id, [])
    
    # Get unique dates
    dates = sorted(set(entry.get('date') for entry in box_entries if entry.get('date')))
    
    # Filter by days if specified
    if days:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        dates = [d for d in dates if d >= cutoff_date]
    
    # Build rank history
    rank_history = []
    for date in dates:
        if date in monthly_rankings and box_id in monthly_rankings[date]:
            rank_history.append({
                'date': date,
                'rank': monthly_rankings[date][box_id],
            })
    
    return rank_history


def get_all_boxes_for_date(date: str) -> List[Dict[str, Any]]:
    """Get all boxes with their data for a specific date"""
    historical_data = load_historical_entries()
    boxes_for_date = []
    
    for box_id, entries in historical_data.items():
        # Find entry for this date
        entry = next((e for e in entries if e.get('date') == date), None)
        if entry:
            boxes_for_date.append({
                'box_id': box_id,
                'date': date,
                'floor_price_usd': entry.get('floor_price_usd'),
                'active_listings_count': entry.get('active_listings_count'),
                'boxes_sold_per_day': entry.get('boxes_sold_per_day'),
            })
    
    return boxes_for_date


def get_rolling_volume_sum(box_id: str, days: int = 30) -> Optional[float]:
    """
    Calculate actual rolling volume sum by summing STORED daily_volume_usd 
    values for the specified number of days.
    
    IMPORTANT: Only uses actual recorded data, no interpolation.
    
    Args:
        box_id: UUID of the booster box
        days: Number of days to sum (7 for 7d, 30 for 30d)
    
    Returns:
        Total volume in USD over the period, or None if no data
    """
    # Get RAW stored data (not calculated)
    entries = get_box_historical_data(box_id)
    
    if not entries:
        return None
    
    # Sort by date
    entries.sort(key=lambda x: x.get('date', ''))
    
    # Get cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Filter to entries within the time period
    recent_entries = [e for e in entries if e.get('date', '') >= cutoff_date]
    
    if not recent_entries:
        return None  # No data in this time period
    
    # Sum ONLY actual captured daily volumes
    # No fallback calculations - only use real recorded data
    total_volume = 0.0
    
    for entry in recent_entries:
        # ONLY use stored daily_volume_usd - this comes from actual screenshot captures
        daily_vol = entry.get('daily_volume_usd', 0) or 0
        total_volume += daily_vol
    
    # Return actual recorded volume only
    return round(total_volume, 2) if total_volume > 0 else None


def get_box_volume_metrics(box_id: str) -> dict:
    """
    Get all volume metrics for a box in one call.
    
    Returns:
        Dictionary with:
        - daily_volume_usd: Latest 24h volume
        - volume_7d: Rolling 7-day sum
        - volume_30d: Rolling 30-day sum
        - unified_volume_7d_ema: 7-day EMA (for smoothing)
    """
    price_history = get_box_price_history(box_id, days=90, one_per_month=False)
    
    if not price_history:
        return {
            'daily_volume_usd': None,
            'volume_7d': None,
            'volume_30d': None,
            'unified_volume_7d_ema': None,
        }
    
    latest = price_history[-1]
    
    return {
        'daily_volume_usd': latest.get('daily_volume_usd'),
        'volume_7d': get_rolling_volume_sum(box_id, 7),
        'volume_30d': get_rolling_volume_sum(box_id, 30),
        'unified_volume_7d_ema': latest.get('unified_volume_7d_ema'),
    }


def get_all_boxes_latest_for_leaderboard(box_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Batch load latest snapshot + derived metrics for many boxes in one DB hit.
    Used by /booster-boxes leaderboard to avoid N per-box historical calls.
    Returns {box_id: {floor_price_usd, daily_volume_usd, unified_volume_7d_ema, unified_volume_usd,
             volume_7d, volume_30d, boxes_sold_30d_avg, floor_price_30d_change_pct, ...}}.
    """
    try:
        from app.services.db_historical_reader import get_all_boxes_historical_entries_from_db
        all_entries = get_all_boxes_historical_entries_from_db(box_ids)
    except Exception:
        all_entries = {}
    out: Dict[str, Dict[str, Any]] = {}
    cutoff_7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cutoff_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    for box_id, entries in all_entries.items():
        if not entries:
            out[box_id] = {}
            continue
        entries = sorted(entries, key=lambda x: x.get('date', ''))
        latest = entries[-1]
        recent_7 = [e for e in entries if (e.get('date') or '') >= cutoff_7]
        recent_30 = [e for e in entries if (e.get('date') or '') >= cutoff_30]
        volume_7d = None
        if recent_7:
            s = sum((e.get('daily_volume_usd') or 0) for e in recent_7)
            volume_7d = round(s, 2) if s > 0 else None
        volume_30d = None
        if recent_30:
            s = sum((e.get('daily_volume_usd') or 0) for e in recent_30)
            volume_30d = round(s, 2) if s > 0 else None
        boxes_sold_30d_avg = None
        if recent_30:
            vals = [(e.get('boxes_sold_per_day') or e.get('boxes_sold_today') or 0) for e in recent_30]
            boxes_sold_30d_avg = round(sum(vals) / len(vals), 2) if vals else None
        monthly = filter_to_one_per_month(entries)
        floor_price_30d_change_pct = None
        if len(monthly) >= 2:
            curr = monthly[-1].get('floor_price_usd')
            prev = monthly[-2].get('floor_price_usd')
            if curr and curr > 0 and prev and prev > 0:
                floor_price_30d_change_pct = round(((curr - prev) / prev) * 100, 2)
        out[box_id] = {
            'floor_price_usd': latest.get('floor_price_usd'),
            'daily_volume_usd': latest.get('daily_volume_usd'),
            'unified_volume_7d_ema': latest.get('unified_volume_7d_ema'),
            'unified_volume_usd': latest.get('unified_volume_usd'),
            'volume_7d': volume_7d,
            'volume_30d': volume_30d,
            'boxes_sold_30d_avg': boxes_sold_30d_avg,
            'floor_price_30d_change_pct': floor_price_30d_change_pct,
            'boxes_sold_per_day': latest.get('boxes_sold_per_day') or latest.get('boxes_sold_today'),
            'boxes_added_today': latest.get('boxes_added_today'),
            'active_listings_count': latest.get('active_listings_count'),
        }
    return out
