"""
Automated Screenshot Processing Pipeline
Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())


Complete end-to-end automation for processing screenshot data
"""

import sys
import asyncio
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select

# Import services
from scripts.data_extraction_formatter import data_extraction_formatter
from app.services.data_filtering import data_filtering_service
from app.services.duplicate_detection import duplicate_detection_service
from scripts.metrics_calculator import metrics_calculator
from scripts.historical_data_manager import historical_data_manager
from scripts.manual_data_entry import get_box_by_name


class AutomatedScreenshotProcessor:
    """Complete automated processing pipeline for screenshot data"""
    
    def __init__(self):
        self.historical_manager = historical_data_manager
    
    async def process_screenshot_data(
        self,
        raw_data: Dict[str, Any],
        box_name: str,
        entry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete automated processing pipeline
        
        Args:
            raw_data: AI-extracted data from screenshot
            box_name: Name of the booster box
            entry_date: Date for this entry (ISO format, defaults to today)
        
        Returns:
            Processing result with success status and details
        """
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        result = {
            "success": False,
            "box_name": box_name,
            "entry_date": entry_date,
            "steps": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Format extracted data
            formatted_data = data_extraction_formatter.format_extracted_data(
                raw_data=raw_data,
                box_name=box_name,
                entry_date=entry_date
            )
            result["steps"]["formatting"] = "success"
            
            # Step 2: Get box from database
            async with AsyncSessionLocal() as db:
                box = await get_box_by_name(db, box_name)
                if not box:
                    result["errors"].append(f"Box '{box_name}' not found in database")
                    return result
                
                result["box_id"] = str(box.id)
                result["steps"]["box_lookup"] = "success"
                
                # Step 3: Get existing listings and sales for duplicate detection
                existing_listings, existing_sales = await self._get_existing_listings_sales(
                    db, box.id
                )
                
                # Step 4: Apply filters
                current_floor_price = formatted_data.get("floor_price_usd")
                filtered_listings = data_filtering_service.filter_listings(
                    listings=formatted_data.get("listings", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                filtered_sales = data_filtering_service.filter_sales(
                    sales=formatted_data.get("sales", []),
                    box_name=box_name,
                    current_floor_price=current_floor_price
                )
                result["steps"]["filtering"] = {
                    "listings_before": len(formatted_data.get("listings", [])),
                    "listings_after": len(filtered_listings),
                    "sales_before": len(formatted_data.get("sales", [])),
                    "sales_after": len(filtered_sales)
                }
                
                # Step 5: Detect duplicates
                new_listings, updated_listings, duplicate_listings = \
                    duplicate_detection_service.detect_listing_duplicates(
                        new_listings=filtered_listings,
                        existing_listings=existing_listings
                    )
                new_sales, duplicate_sales = \
                    duplicate_detection_service.detect_sale_duplicates(
                        new_sales=filtered_sales,
                        existing_sales=existing_sales
                    )
                result["steps"]["duplicate_detection"] = {
                    "new_listings": len(new_listings),
                    "updated_listings": len(updated_listings),
                    "duplicate_listings": len(duplicate_listings),
                    "new_sales": len(new_sales),
                    "duplicate_sales": len(duplicate_sales)
                }
                
                # Step 6: Aggregate data (only count listings within 20% of floor price)
                # Use filtered_listings for active_listings_count (all current market listings)
                # Use new_listings for boxes_added_today (only new listings)
                aggregated = self._aggregate_data(
                    new_listings=filtered_listings,  # Count all filtered listings, not just new ones
                    new_sales=new_sales,
                    entry_date=entry_date,
                    floor_price=formatted_data.get("floor_price_usd")
                )
                # Track boxes_added_today separately (only new listings)
                aggregated["boxes_added_today"] = len(new_listings)
                result["steps"]["aggregation"] = "success"
                
                # Step 7: Get historical data for calculations
                # Start with JSON data
                historical_entries = self.historical_manager.get_box_history(str(box.id))
                
                # CRITICAL: Include database entries (screenshot data) for accurate averaging
                # Query database for all existing metrics entries to ensure averages include all screenshot data
                db_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == box.id
                ).order_by(UnifiedBoxMetrics.metric_date)
                db_result = await db.execute(db_stmt)
                db_metrics = db_result.scalars().all()
                
                # Convert database entries to historical format and merge with JSON entries
                db_entries_by_date = {}
                for metric in db_metrics:
                    date_str = metric.metric_date.isoformat()
                    # Only include if not already in historical_entries (avoid duplicates)
                    if not any(e.get('date') == date_str for e in historical_entries):
                        db_entries_by_date[date_str] = {
                            "date": date_str,
                            "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                            "active_listings_count": metric.active_listings_count,
                            "boxes_sold_today": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "boxes_sold_per_day": float(metric.boxes_sold_per_day) if metric.boxes_sold_per_day else 0,
                            "daily_volume_usd": float(metric.unified_volume_usd) if metric.unified_volume_usd else 0,
                            "boxes_added_today": metric.boxes_added_today or 0,
                            "unified_volume_7d_ema": float(metric.unified_volume_7d_ema) if metric.unified_volume_7d_ema else None,
                        }
                    else:
                        # Update existing entry with database data (database is more accurate for screenshot data)
                        for e in historical_entries:
                            if e.get('date') == date_str:
                                if metric.boxes_sold_per_day is not None:
                                    e['boxes_sold_today'] = float(metric.boxes_sold_per_day)
                                    e['boxes_sold_per_day'] = float(metric.boxes_sold_per_day)
                                if metric.unified_volume_usd is not None:
                                    e['daily_volume_usd'] = float(metric.unified_volume_usd)
                                break
                
                # Add database entries that don't exist in JSON
                for date_str, entry in db_entries_by_date.items():
                    historical_entries.append(entry)
                
                # Add current entry to historical data (for calculations)
                current_entry = {
                    "date": entry_date,
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "boxes_sold_per_day": aggregated["boxes_sold_today"],  # Use actual sales count for this day
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", [])
                }
                historical_entries.append(current_entry)
                
                # Sort by date to ensure proper averaging
                historical_entries.sort(key=lambda x: x.get('date', ''))
                
                # Step 8: Calculate all metrics
                calculated_metrics = metrics_calculator.calculate_daily_metrics(
                    historical_data=historical_entries
                )
                result["steps"]["calculations"] = "success"
                result["metrics"] = calculated_metrics
                
                # Step 9: Save to database
                save_result = await self._save_to_database(
                    db=db,
                    box=box,
                    entry_date=entry_date,
                    calculated_metrics=calculated_metrics,
                    aggregated_data=aggregated
                )
                result["steps"]["database_save"] = save_result
                
                # Step 10: Save to historical data manager
                historical_entry = {
                    "date": entry_date,
                    "source": "screenshot",
                    "data_type": "combined",
                    "floor_price_usd": formatted_data.get("floor_price_usd"),
                    "active_listings_count": aggregated["active_listings_count"],
                    "boxes_sold_today": aggregated["boxes_sold_today"],
                    "daily_volume_usd": aggregated["daily_volume_usd"],
                    "boxes_added_today": len(new_listings),
                    "price_ladder": formatted_data.get("price_ladder", []),
                    "raw_listings": new_listings,
                    "raw_sales": new_sales
                }
                self.historical_manager.add_entry(str(box.id), historical_entry)
                result["steps"]["historical_save"] = "success"
                
                # Recalculate active_listings_count from all listings for this date
                # Include the listings we just added + any existing ones for this date
                all_listings_for_date = list(new_listings) if new_listings else []  # Start with current listings
                floor_price_for_counting = formatted_data.get("floor_price_usd")
                
                # Also collect from existing historical entries for this date
                all_entries = self.historical_manager.get_box_history(str(box.id))
                for e in all_entries:
                    if str(e.get("date")) == str(entry_date):  # Ensure date match
                        if e.get("raw_listings"):
                            # Add listings that aren't already in our list (avoid duplicates)
                            existing_prices = {(l.get("price", 0), l.get("shipping", 0)) for l in all_listings_for_date}
                            for listing in e.get("raw_listings", []):
                                listing_key = (listing.get("price", 0) or 0, listing.get("shipping", 0) or 0)
                                if listing_key not in existing_prices:
                                    all_listings_for_date.append(listing)
                                    existing_prices.add(listing_key)
                        # Use floor price from entry with listings (prioritize current market)
                        if e.get("raw_listings") and e.get("floor_price_usd"):
                            floor_price_for_counting = e.get("floor_price_usd")
                
                # If no floor price yet, calculate from lowest listing
                if (not floor_price_for_counting or floor_price_for_counting <= 0) and all_listings_for_date:
                    listing_totals = [
                        (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                        for l in all_listings_for_date
                    ]
                    if listing_totals:
                        floor_price_for_counting = min(listing_totals)
                
                # Count listings within 20% of floor price
                if floor_price_for_counting and floor_price_for_counting > 0:
                    max_price = floor_price_for_counting * 1.20
                    listings_within_20pct = [
                        l for l in all_listings_for_date
                        if (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0) <= max_price
                    ]
                    aggregated["active_listings_count"] = len(listings_within_20pct)
                elif all_listings_for_date:
                    # If no floor price but we have listings, count all (shouldn't happen)
                    aggregated["active_listings_count"] = len(all_listings_for_date)
                
                result["success"] = True
                result["message"] = f"Successfully processed screenshot data for {box_name}"
                
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def _get_existing_listings_sales(
        self,
        db,
        box_id: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Get existing listings and sales from historical data"""
        historical_entries = self.historical_manager.get_box_history(str(box_id))
        
        existing_listings = []
        existing_sales = []
        
        for entry in historical_entries:
            # Extract listings
            if "raw_listings" in entry:
                existing_listings.extend(entry["raw_listings"])
            # Extract sales
            if "raw_sales" in entry:
                existing_sales.extend(entry["raw_sales"])
        
        return existing_listings, existing_sales
    
    def _aggregate_data(
        self,
        new_listings: List[Dict[str, Any]],
        new_sales: List[Dict[str, Any]],
        entry_date: str,
        floor_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Aggregate filtered and deduplicated data"""
        # Calculate floor price from listings if not provided
        # Floor price = lowest (price + shipping) from all listings
        if not floor_price or floor_price <= 0:
            if new_listings:
                # Find lowest listing price (price + shipping)
                listing_totals = [
                    (l.get("price", 0) or 0) + (l.get("shipping", 0) or 0)
                    for l in new_listings
                ]
                if listing_totals:
                    floor_price = min(listing_totals)
        
        # Only count listings within 20% of floor price
        listings_within_20pct = []
        if floor_price and floor_price > 0:
            max_price = floor_price * 1.20  # 20% above floor
            for listing in new_listings:
                listing_price = listing.get("price", 0) or 0
                listing_shipping = listing.get("shipping", 0) or 0
                total_price = listing_price + listing_shipping
                if total_price <= max_price:
                    listings_within_20pct.append(listing)
        else:
            # If still no floor price (no listings), count all (should be empty)
            listings_within_20pct = new_listings
        
        aggregated = {
            "active_listings_count": len(listings_within_20pct),
            "boxes_sold_today": 0,
            "daily_volume_usd": 0.0
        }
        
        # Aggregate sales for current day
        for sale in new_sales:
            if sale.get("date") == entry_date:
                aggregated["boxes_sold_today"] += sale.get("quantity", 0)
                aggregated["daily_volume_usd"] += sale.get("price", 0) * sale.get("quantity", 0)
        
        return aggregated
    
    async def _save_to_database(
        self,
        db,
        box: BoosterBox,
        entry_date: str,
        calculated_metrics: Dict[str, Any],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save all calculated metrics to database"""
        try:
            date_obj = date.fromisoformat(entry_date)
            
            # Check if record exists
            stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box.id,
                UnifiedBoxMetrics.metric_date == date_obj
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # Prepare metrics dictionary
            metrics_dict = {
                "floor_price_usd": calculated_metrics.get("floor_price_usd"),
                "floor_price_1d_change_pct": calculated_metrics.get("floor_price_1d_change_pct"),
                "floor_price_30d_change_pct": calculated_metrics.get("floor_price_30d_change_pct"),
                "unified_volume_usd": calculated_metrics.get("unified_volume_usd") or aggregated_data.get("daily_volume_usd"),
                "unified_volume_7d_ema": calculated_metrics.get("unified_volume_7d_ema"),
                "unified_volume_30d_sma": calculated_metrics.get("unified_volume_30d_sma"),
                "volume_mom_change_pct": calculated_metrics.get("volume_mom_change_pct"),
                "active_listings_count": aggregated_data.get("active_listings_count"),
                "boxes_sold_per_day": calculated_metrics.get("boxes_sold_per_day") or aggregated_data.get("boxes_sold_today"),
                "boxes_sold_30d_avg": calculated_metrics.get("boxes_sold_30d_avg"),
                "boxes_added_today": aggregated_data.get("boxes_added_today", 0),
                "avg_boxes_added_per_day": calculated_metrics.get("avg_boxes_added_per_day"),
                "days_to_20pct_increase": calculated_metrics.get("days_to_20pct_increase"),
                "expected_days_to_sell": calculated_metrics.get("expected_days_to_sell"),
                "liquidity_score": calculated_metrics.get("liquidity_score"),
                "visible_market_cap_usd": calculated_metrics.get("visible_market_cap_usd"),
                "listed_percentage": calculated_metrics.get("listed_percentage"),
            }
            
            if existing:
                # Update existing record
                for key, value in metrics_dict.items():
                    if value is not None:
                        setattr(existing, key, Decimal(str(value)) if isinstance(value, (int, float)) else value)
                
                await db.commit()
                return {"action": "updated", "success": True}
            else:
                # Create new record
                new_metrics = UnifiedBoxMetrics(
                    booster_box_id=box.id,
                    metric_date=date_obj,
                    **{k: Decimal(str(v)) if isinstance(v, (int, float)) and v is not None else v 
                       for k, v in metrics_dict.items() if v is not None}
                )
                
                db.add(new_metrics)
                await db.commit()
                return {"action": "created", "success": True}
                
        except Exception as e:
            await db.rollback()
            return {"action": "error", "success": False, "error": str(e)}


# Global instance
automated_processor = AutomatedScreenshotProcessor()


async def process_screenshot_data(
    raw_data: Dict[str, Any],
    box_name: str,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for processing screenshot data
    
    Usage:
        result = await process_screenshot_data(
            raw_data={
                "floor_price": 100.0,
                "floor_price_shipping": 5.0,
                "listings": [...],
                "sales": [...]
            },
            box_name="OP-01",
            entry_date="2025-01-03"
        )
    """
    return await automated_processor.process_screenshot_data(
        raw_data=raw_data,
        box_name=box_name,
        entry_date=entry_date
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example raw data structure
        example_data = {
            "floor_price": 100.0,
            "floor_price_shipping": 5.0,
            "listings": [
                {
                    "price": 105.0,
                    "shipping": 5.0,
                    "quantity": 2,
                    "seller": "seller1",
                    "title": "OP-01 Booster Box",
                    "platform": "ebay"
                }
            ],
            "sales": [
                {
                    "price": 110.0,
                    "shipping": 5.0,
                    "quantity": 1,
                    "date": "2025-01-03",
                    "seller": "seller2",
                    "title": "OP-01 Booster Box",
                    "platform": "tcgplayer"
                }
            ]
        }
        
        result = await process_screenshot_data(
            raw_data=example_data,
            box_name="OP-01",
            entry_date="2025-01-03"
        )
        
        print("\n" + "=" * 60)
        print("Processing Result")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
        print(f"\nSteps: {result.get('steps', {})}")
        print(f"\nCalculated Metrics: {result.get('metrics', {})}")
    
    asyncio.run(main())

