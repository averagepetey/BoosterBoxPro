"""
Historical Data Service
Handles loading and processing historical data for boxes
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict


def load_historical_entries() -> Dict[str, List[Dict[str, Any]]]:
    """Load all historical entries from JSON file"""
    historical_file = Path(__file__).parent.parent.parent / "data" / "historical_entries.json"
    
    if not historical_file.exists():
        return {}
    
    with open(historical_file, 'r') as f:
        return json.load(f)


def get_box_historical_data(box_id: str) -> List[Dict[str, Any]]:
    """Get historical data for a specific box"""
    historical_data = load_historical_entries()
    return historical_data.get(box_id, [])


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
        boxes_sold_per_day = entry.get('boxes_sold_per_day', 0)
        
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
        # Period volume = floor_price * units_sold_count (for the time period between entries)
        unified_volume_usd = None
        if floor_price and units_sold_count and units_sold_count > 0:
            # Use period volume (price * units sold in that period)
            unified_volume_usd = floor_price * units_sold_count
        elif floor_price and boxes_sold_per_day:
            # Fallback to daily volume if no period calculation available
            unified_volume_usd = floor_price * boxes_sold_per_day
        
        # Ensure date is in correct format (YYYY-MM-DD)
        date_str = entry.get('date')
        if date_str:
            # Parse and reformat to ensure consistency
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                pass  # Keep original if parsing fails
        
        # Calculate 7-day EMA of volume
        # EMA = (Current Value * (2 / (Period + 1))) + (Previous EMA * (1 - (2 / (Period + 1))))
        unified_volume_7d_ema = None
        if unified_volume_usd:
            if i == 0:
                # First entry: use current volume as initial EMA
                unified_volume_7d_ema = unified_volume_usd
            else:
                # Get previous EMA from result
                prev_ema = result[-1].get('unified_volume_7d_ema') if result else None
                
                if prev_ema:
                    # Calculate EMA with smoothing factor for 7-day period
                    # For weekly data, we'll use a smoothing factor that approximates 7 days
                    alpha = 2 / (7 + 1)  # Smoothing factor for 7-day EMA
                    unified_volume_7d_ema = (unified_volume_usd * alpha) + (prev_ema * (1 - alpha))
                else:
                    # Fallback: use current volume
                    unified_volume_7d_ema = unified_volume_usd
        
        result.append({
            'date': date_str,
            'floor_price_usd': floor_price,
            'floor_price_1d_change_pct': floor_price_1d_change_pct,
            'active_listings_count': entry.get('active_listings_count'),
            'boxes_sold_per_day': boxes_sold_per_day,
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
                    
                    # Recalculate volume based on new units sold
                    floor_price = entry.get('floor_price_usd', 0)
                    if floor_price > 0 and units_sold_count > 0:
                        result[i]['unified_volume_usd'] = floor_price * units_sold_count
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
    Returns the average of boxes_sold_per_day from entries in the last 30 days.
    Includes all values (including zeros) for a true 30-day average.
    """
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
    daily_sales = [e.get('boxes_sold_per_day', 0) or 0 for e in recent_entries]
    
    if not daily_sales:
        return 0.0
    
    # Calculate average of all values
    avg_sales = sum(daily_sales) / len(daily_sales)
    return round(avg_sales, 2)


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

