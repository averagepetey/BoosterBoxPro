"""
Raw Data Aggregator Service
Aggregates raw sales and listing data into unified metrics
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text

from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.metrics_calculator import MetricsCalculator


class RawDataAggregator:
    """Service for aggregating raw sales and listing data into unified metrics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_calculator = MetricsCalculator(db)
    
    async def aggregate_listings_to_metrics(
        self,
        box_id: UUID,
        snapshot_date: date
    ) -> Optional[Dict]:
        """
        Aggregate listing data from tcg_listings_raw into unified metrics
        
        Calculates:
        - Floor price (minimum listed_price_usd)
        - Active listings count (sum of quantities)
        - Visible market cap (floor_price × total_quantity)
        
        Args:
            box_id: Booster box UUID
            snapshot_date: Date to aggregate for
            
        Returns:
            Dictionary with aggregated metrics or None if no listings
        """
        # Query to aggregate listings for this box and date
        query = text("""
            SELECT 
                MIN(listed_price_usd) as floor_price,
                SUM(quantity) as active_listings_count,
                COUNT(*) as listing_count,
                AVG(listed_price_usd) as avg_price
            FROM tcg_listings_raw
            WHERE booster_box_id = :box_id
            AND snapshot_date = :snapshot_date
            AND is_active = true
        """)
        
        result = await self.db.execute(
            query,
            {"box_id": str(box_id), "snapshot_date": snapshot_date}
        )
        
        row = result.fetchone()
        
        if not row or row[0] is None:  # No floor price means no listings
            return None
        
        floor_price = Decimal(str(row[0])) if row[0] else None
        active_listings_count = int(row[1]) if row[1] else 0
        
        if not floor_price or active_listings_count == 0:
            return None
        
        # Calculate market cap
        visible_market_cap = floor_price * Decimal(str(active_listings_count))
        
        return {
            "floor_price_usd": floor_price,
            "active_listings_count": active_listings_count,
            "visible_market_cap_usd": visible_market_cap,
            "listing_count": int(row[2]) if row[2] else 0,
            "avg_price_usd": Decimal(str(row[3])) if row[3] else None,
        }
    
    async def aggregate_sales_to_metrics(
        self,
        box_id: UUID,
        sale_date: date
    ) -> Optional[Dict]:
        """
        Aggregate sales data from ebay_sales_raw into unified metrics
        
        Calculates:
        - Daily volume (sum of sold_price_usd × quantity)
        - Units sold count (sum of quantities)
        - Average sold price
        - Boxes sold per day
        
        Args:
            box_id: Booster box UUID
            sale_date: Date to aggregate for
            
        Returns:
            Dictionary with aggregated metrics or None if no sales
        """
        # Query to aggregate sales for this box and date
        query = text("""
            SELECT 
                SUM(sold_price_usd * quantity) as daily_volume_usd,
                SUM(quantity) as units_sold_count,
                COUNT(*) as sales_count,
                AVG(sold_price_usd) as avg_sold_price,
                MIN(sold_price_usd) as min_sold_price,
                MAX(sold_price_usd) as max_sold_price
            FROM ebay_sales_raw
            WHERE booster_box_id = :box_id
            AND sale_date = :sale_date
        """)
        
        result = await self.db.execute(
            query,
            {"box_id": str(box_id), "sale_date": sale_date}
        )
        
        row = result.fetchone()
        
        if not row or row[0] is None:  # No volume means no sales
            return None
        
        daily_volume_usd = Decimal(str(row[0])) if row[0] else Decimal('0')
        units_sold_count = int(row[1]) if row[1] else 0
        
        if daily_volume_usd == 0 and units_sold_count == 0:
            return None
        
        return {
            "unified_volume_usd": daily_volume_usd,
            "units_sold_count": units_sold_count,
            "boxes_sold_per_day": Decimal(str(units_sold_count)),  # Same as units sold for booster boxes
            "sales_count": int(row[2]) if row[2] else 0,
            "avg_sold_price_usd": Decimal(str(row[3])) if row[3] else None,
            "min_sold_price_usd": Decimal(str(row[4])) if row[4] else None,
            "max_sold_price_usd": Decimal(str(row[5])) if row[5] else None,
        }
    
    async def create_unified_metrics_from_raw_data(
        self,
        box_id: UUID,
        target_date: date,
        use_listings: bool = True,
        use_sales: bool = True
    ) -> Optional[Dict]:
        """
        Create unified metrics from raw listings and/or sales data
        
        Aggregates raw data and creates/updates unified metrics record
        
        Args:
            box_id: Booster box UUID
            target_date: Date to create metrics for
            use_listings: Whether to use tcg_listings_raw data
            use_sales: Whether to use ebay_sales_raw data
            
        Returns:
            Dictionary with created/updated metrics or None
        """
        metrics_data = {}
        
        # Aggregate listings if requested
        if use_listings:
            listing_metrics = await self.aggregate_listings_to_metrics(box_id, target_date)
            if listing_metrics:
                metrics_data.update(listing_metrics)
        
        # Aggregate sales if requested
        if use_sales:
            sales_metrics = await self.aggregate_sales_to_metrics(box_id, target_date)
            if sales_metrics:
                metrics_data.update(sales_metrics)
        
        if not metrics_data:
            return None
        
        # Ensure we have required fields
        if "booster_box_id" not in metrics_data:
            metrics_data["booster_box_id"] = box_id
        if "metric_date" not in metrics_data:
            metrics_data["metric_date"] = target_date
        
        # Get or create unified metrics record
        existing = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if existing:
            # Update existing record with aggregated data
            for key, value in metrics_data.items():
                if key not in ["booster_box_id", "metric_date"]:
                    setattr(existing, key, value)
            
            await self.db.commit()
            await self.db.refresh(existing)
            
            # Calculate derived metrics
            updated = await self.metrics_calculator.update_metrics_with_calculations(
                box_id, target_date
            )
            
            return updated
        else:
            # Create new record
            metrics_data["booster_box_id"] = box_id
            metrics_data["metric_date"] = target_date
            
            created = await UnifiedMetricsRepository.create_or_update(
                self.db, metrics_data
            )
            
            # Calculate derived metrics
            updated = await self.metrics_calculator.update_metrics_with_calculations(
                box_id, target_date
            )
            
            return updated

