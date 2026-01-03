"""
Metrics Calculator
Calculates derived metrics from raw sales and listing data
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics


class MetricsCalculator:
    """Calculates metrics from historical raw data"""
    
    def __init__(self):
        pass
    
    def calculate_daily_metrics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate daily metrics from historical data
        
        Args:
            historical_data: List of historical data entries, each with:
                - date: ISO date string
                - floor_price_usd: float or None
                - active_listings_count: int or None
                - boxes_sold_today: int or None
                - daily_volume_usd: float or None
                - boxes_added_today: int or None
        
        Returns:
            Dictionary with calculated metrics
        """
        if not historical_data:
            return {}
        
        # Sort by date
        sorted_data = sorted(historical_data, key=lambda x: x.get("date", ""))
        
        # Get today's data (most recent)
        today_data = sorted_data[-1] if sorted_data else {}
        
        # Calculate averages over different periods
        metrics = {}
        
        # Floor price
        floor_prices = [d.get("floor_price_usd") for d in sorted_data if d.get("floor_price_usd") is not None]
        if floor_prices:
            metrics["floor_price_usd"] = floor_prices[-1]  # Current
            if len(floor_prices) > 1:
                metrics["floor_price_1d_change_pct"] = self._calculate_percentage_change(
                    floor_prices[-2], floor_prices[-1]
                )
            else:
                metrics["floor_price_1d_change_pct"] = 0.0
        
        # Daily volume - use provided or calculate from sales
        volumes = [d.get("daily_volume_usd") for d in sorted_data if d.get("daily_volume_usd") is not None]
        if volumes:
            metrics["daily_volume_usd"] = volumes[-1]
            # Calculate 7-day EMA for volume
            if len(volumes) >= 7:
                metrics["unified_volume_7d_ema"] = self._calculate_ema(volumes[-7:], alpha=0.3)
            else:
                metrics["unified_volume_7d_ema"] = statistics.mean(volumes) if volumes else None
        
        # Units sold
        units_sold = [d.get("boxes_sold_today") or d.get("units_sold_count") for d in sorted_data]
        units_sold = [u for u in units_sold if u is not None]
        if units_sold:
            metrics["units_sold_count"] = units_sold[-1]  # Today's sales
            metrics["boxes_sold_per_day"] = statistics.mean(units_sold[-30:]) if len(units_sold) > 0 else units_sold[-1]
            metrics["boxes_sold_30d_avg"] = statistics.mean(units_sold[-30:]) if len(units_sold) >= 30 else statistics.mean(units_sold) if units_sold else None
        
        # Active listings
        listings = [d.get("active_listings_count") for d in sorted_data if d.get("active_listings_count") is not None]
        if listings:
            metrics["active_listings_count"] = listings[-1]
        
        # Boxes added per day
        boxes_added = [d.get("boxes_added_today") for d in sorted_data if d.get("boxes_added_today") is not None]
        if boxes_added:
            metrics["boxes_added_today"] = boxes_added[-1]
            metrics["avg_boxes_added_per_day"] = statistics.mean(boxes_added[-7:]) if len(boxes_added) >= 7 else statistics.mean(boxes_added) if boxes_added else None
        
        # Listed percentage
        if metrics.get("active_listings_count") is not None and today_data.get("estimated_total_supply"):
            metrics["listed_percentage"] = (metrics["active_listings_count"] / today_data["estimated_total_supply"]) * 100
        elif metrics.get("active_listings_count") is not None and sorted_data:
            # Try to find estimated supply from any entry
            for d in reversed(sorted_data):
                if d.get("estimated_total_supply"):
                    metrics["listed_percentage"] = (metrics["active_listings_count"] / d["estimated_total_supply"]) * 100
                    break
        
        # Market cap
        if metrics.get("floor_price_usd") and today_data.get("estimated_total_supply"):
            metrics["visible_market_cap_usd"] = metrics["floor_price_usd"] * today_data["estimated_total_supply"]
        elif metrics.get("floor_price_usd") and sorted_data:
            for d in reversed(sorted_data):
                if d.get("estimated_total_supply"):
                    metrics["visible_market_cap_usd"] = metrics["floor_price_usd"] * d["estimated_total_supply"]
                    break
        
        # Liquidity score (simplified calculation)
        if metrics.get("active_listings_count") and metrics.get("boxes_sold_per_day"):
            if metrics["boxes_sold_per_day"] > 0:
                metrics["liquidity_score"] = min(1.0, metrics["active_listings_count"] / (metrics["boxes_sold_per_day"] * 7))
            else:
                metrics["liquidity_score"] = 0.0
        
        # Days to 20% increase (simplified)
        if metrics.get("floor_price_1d_change_pct") and metrics["floor_price_1d_change_pct"] > 0:
            metrics["days_to_20pct_increase"] = 20.0 / metrics["floor_price_1d_change_pct"]
        else:
            metrics["days_to_20pct_increase"] = None
        
        # Expected days to sell
        if metrics.get("active_listings_count") and metrics.get("boxes_sold_per_day"):
            if metrics["boxes_sold_per_day"] > 0:
                metrics["expected_days_to_sell"] = metrics["active_listings_count"] / metrics["boxes_sold_per_day"]
            else:
                metrics["expected_days_to_sell"] = None
        
        return metrics
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / old_value) * 100
    
    def _calculate_ema(self, values: List[float], alpha: float = 0.3) -> float:
        """Calculate Exponential Moving Average"""
        if not values:
            return 0.0
        
        ema = values[0]
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema
        return ema
    
    def calculate_volume_from_sales(self, sales_data: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculate daily volume from individual sales
        
        Args:
            sales_data: List of sales, each with:
                - price_usd: float
                - quantity: int (default 1)
                - date: ISO date string
        
        Returns:
            Total volume in USD for today
        """
        today = date.today().isoformat()
        today_sales = [s for s in sales_data if s.get("date") == today]
        
        if not today_sales:
            return None
        
        total_volume = sum(
            sale.get("price_usd", 0) * sale.get("quantity", 1)
            for sale in today_sales
        )
        
        return total_volume
    
    def identify_new_data(self, existing_entries: List[Dict[str, Any]], new_screenshot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify which data from a screenshot is new vs already exists
        
        Args:
            existing_entries: List of existing data entries for this box
            new_screenshot_data: Data extracted from new screenshot
        
        Returns:
            Dictionary with:
                - is_new: bool
                - new_fields: List of field names that are new
                - existing_fields: List of field names that already exist
                - needs_update: bool
                - update_reason: str
        """
        if not existing_entries:
            return {
                "is_new": True,
                "new_fields": list(new_screenshot_data.keys()),
                "existing_fields": [],
                "needs_update": True,
                "update_reason": "No existing data found"
            }
        
        # Get most recent entry
        sorted_entries = sorted(existing_entries, key=lambda x: x.get("date", ""), reverse=True)
        latest_entry = sorted_entries[0]
        
        new_fields = []
        existing_fields = []
        differences = {}
        
        # Compare each field
        for field, new_value in new_screenshot_data.items():
            if new_value is None:
                continue
            
            existing_value = latest_entry.get(field)
            
            if existing_value is None:
                new_fields.append(field)
            elif self._values_differ(existing_value, new_value, field):
                new_fields.append(field)
                differences[field] = {
                    "existing": existing_value,
                    "new": new_value
                }
            else:
                existing_fields.append(field)
        
        needs_update = len(new_fields) > 0 or len(differences) > 0
        
        if needs_update:
            if len(new_fields) > 0:
                update_reason = f"New data for: {', '.join(new_fields)}"
            else:
                update_reason = f"Updated values for: {', '.join(differences.keys())}"
        else:
            update_reason = "No new or changed data"
        
        return {
            "is_new": len(existing_entries) == 0,
            "new_fields": new_fields,
            "existing_fields": existing_fields,
            "differences": differences,
            "needs_update": needs_update,
            "update_reason": update_reason,
            "latest_entry_date": latest_entry.get("date")
        }
    
    def _values_differ(self, existing: Any, new: Any, field: str) -> bool:
        """Check if two values differ significantly"""
        # Tolerance for numeric fields
        numeric_tolerance = {
            "floor_price_usd": 0.01,
            "daily_volume_usd": 0.01,
            "visible_market_cap_usd": 0.01,
        }.get(field, 0)
        
        if isinstance(existing, (int, float)) and isinstance(new, (int, float)):
            return abs(existing - new) > numeric_tolerance
        
        return existing != new


# Global instance
metrics_calculator = MetricsCalculator()

