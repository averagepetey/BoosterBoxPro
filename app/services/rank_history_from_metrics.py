"""
Rank History Service using Advanced Metrics Data
Calculates rankings from historical_entries.json volume data
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

from app.services.historical_data import load_historical_entries, get_box_price_history


def get_all_boxes() -> List[Dict[str, str]]:
    """Get all boxes from leaderboard.json"""
    data_file = Path(__file__).parent.parent.parent / "data" / "leaderboard.json"
    mock_file = Path(__file__).parent.parent.parent / "mock_data" / "leaderboard.json"
    
    leaderboard_data = None
    if data_file.exists():
        with open(data_file, "r") as f:
            leaderboard_data = json.load(f)
    elif mock_file.exists():
        with open(mock_file, "r") as f:
            leaderboard_data = json.load(f)
    
    if not leaderboard_data:
        return []
    
    return leaderboard_data.get("data", [])


def calculate_ranks_for_date(date_str: str, box_volumes: Dict[str, float]) -> Dict[str, int]:
    """
    Calculate ranks for all boxes on a specific date based on volume
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        box_volumes: Dictionary mapping box_id to unified_volume_7d_ema
        
    Returns:
        Dictionary mapping box_id to rank (1 = highest volume)
    """
    # Filter out boxes with no volume data
    valid_volumes = {box_id: vol for box_id, vol in box_volumes.items() if vol is not None and vol > 0}
    
    if not valid_volumes:
        return {}
    
    # Sort boxes by volume (descending)
    sorted_boxes = sorted(valid_volumes.items(), key=lambda x: x[1], reverse=True)
    
    # Assign ranks (handle ties: same rank for equal volumes, skip next rank)
    ranks = {}
    current_rank = 1
    previous_volume: Optional[float] = None
    
    for box_id, volume in sorted_boxes:
        # If this volume is different from previous, advance to next rank
        if previous_volume is not None and volume != previous_volume:
            current_rank = len(ranks) + 1
        
        ranks[box_id] = current_rank
        previous_volume = volume
    
    return ranks


def get_rank_history_for_box(box_id: str) -> List[Dict[str, Any]]:
    """
    Get rank history for a specific box using Advanced Metrics data
    
    Args:
        box_id: Box UUID as string
        
    Returns:
        List of {date: str, rank: int} dictionaries, sorted by date
    """
    # Get all boxes
    all_boxes = get_all_boxes()
    if not all_boxes:
        return []
    
    # Get historical data for all boxes
    historical_data = load_historical_entries()
    
    # Get all dates that have data for any box
    all_dates = set()
    for box in all_boxes:
        box_id_key = box.get("id")
        if box_id_key in historical_data:
            for entry in historical_data[box_id_key]:
                date_val = entry.get("date")
                if date_val:
                    all_dates.add(date_val)
    
    # Sort dates
    sorted_dates = sorted(all_dates)
    
    # Calculate ranks for each date
    rank_history = []
    
    for date_str in sorted_dates:
        # Get volume data for all boxes on this date
        box_volumes = {}
        
        for box in all_boxes:
            box_id_key = box.get("id")
            if box_id_key in historical_data:
                # Find entry for this date
                for entry in historical_data[box_id_key]:
                    if entry.get("date") == date_str:
                        # Use get_box_price_history to get calculated unified_volume_7d_ema
                        # This ensures we use the same calculation as Advanced Metrics table
                        price_history = get_box_price_history(box_id_key, days=None, one_per_month=False)
                        if price_history:
                            # Find the entry for this date
                            for ph_entry in price_history:
                                if ph_entry.get("date") == date_str:
                                    volume = ph_entry.get("unified_volume_7d_ema")
                                    if volume is not None:
                                        box_volumes[box_id_key] = volume
                                    break
                        break
        
        # Calculate ranks for this date
        date_ranks = calculate_ranks_for_date(date_str, box_volumes)
        
        # Get rank for the requested box
        if box_id in date_ranks:
            rank_history.append({
                "date": date_str,
                "rank": date_ranks[box_id]
            })
    
    return rank_history


def get_rank_history_for_box_optimized(box_id: str) -> List[Dict[str, Any]]:
    """
    Optimized version: Calculate ranks for all dates at once
    
    Args:
        box_id: Box UUID as string
        
    Returns:
        List of {date: str, rank: int} dictionaries, sorted by date
    """
    # Get all boxes
    all_boxes = get_all_boxes()
    if not all_boxes:
        return []
    
    # Get all boxes' price histories (with calculated volumes)
    all_boxes_data: Dict[str, List[Dict[str, Any]]] = {}
    for box in all_boxes:
        box_id_key = box.get("id")
        price_history = get_box_price_history(box_id_key, days=None, one_per_month=False)
        if price_history:
            all_boxes_data[box_id_key] = price_history
    
    # Get all unique dates
    all_dates = set()
    for price_history in all_boxes_data.values():
        for entry in price_history:
            date_val = entry.get("date")
            if date_val:
                all_dates.add(date_val)
    
    sorted_dates = sorted(all_dates)
    
    # Calculate ranks for each date
    rank_history = []
    
    for date_str in sorted_dates:
        # Collect volumes for all boxes on this date
        box_volumes = {}
        for box_id_key, price_history in all_boxes_data.items():
            for entry in price_history:
                if entry.get("date") == date_str:
                    volume = entry.get("unified_volume_7d_ema")
                    if volume is not None:
                        box_volumes[box_id_key] = volume
                    break
        
        # Calculate ranks for this date
        date_ranks = calculate_ranks_for_date(date_str, box_volumes)
        
        # Get rank for the requested box
        if box_id in date_ranks:
            rank_history.append({
                "date": date_str,
                "rank": date_ranks[box_id]
            })
    
    return rank_history


# Use optimized version
get_box_rank_history = get_rank_history_for_box_optimized

