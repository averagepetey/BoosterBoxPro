#!/usr/bin/env python3
"""
Metrics Recalculation Script
Recalculates all derived metrics for historical data

Usage:
    python scripts/recalculate_metrics.py [--box-id <uuid>] [--date <YYYY-MM-DD>] [--all]
"""

import asyncio
import sys
from datetime import date
from uuid import UUID
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings
from app.services.metrics_calculator import MetricsCalculator
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox


async def recalculate_metrics_for_box_and_date(
    db: AsyncSession,
    box_id: UUID,
    target_date: date
) -> bool:
    """
    Recalculate all metrics for a specific box and date
    
    Returns:
        True if successful, False otherwise
    """
    calculator = MetricsCalculator(db)
    
    try:
        # Check if metrics exist for this date
        from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            db, box_id, target_date
        )
        
        if not metrics:
            print(f"  ⚠️  No metrics found for box {box_id} on {target_date}")
            return False
        
        # Recalculate all derived metrics
        updated = await calculator.update_metrics_with_calculations(
            box_id, target_date
        )
        
        if updated:
            print(f"  ✅ Recalculated metrics for {target_date}")
            return True
        else:
            print(f"  ❌ Failed to recalculate for {target_date}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error recalculating: {e}")
        return False


async def recalculate_all_metrics_for_box(
    db: AsyncSession,
    box_id: UUID
) -> tuple[int, int]:
    """
    Recalculate all metrics for a specific box across all dates
    
    Returns:
        Tuple of (successful_count, failed_count)
    """
    # Get all dates with metrics for this box
    result = await db.execute(
        select(UnifiedBoxMetrics.metric_date)
        .where(UnifiedBoxMetrics.booster_box_id == box_id)
        .order_by(UnifiedBoxMetrics.metric_date.asc())
        .distinct()
    )
    
    dates = [row[0] for row in result.all()]
    
    if not dates:
        print(f"⚠️  No metrics found for box {box_id}")
        return (0, 0)
    
    print(f"📊 Found {len(dates)} dates with metrics for box {box_id}")
    
    successful = 0
    failed = 0
    
    for target_date in dates:
        success = await recalculate_metrics_for_box_and_date(db, box_id, target_date)
        if success:
            successful += 1
        else:
            failed += 1
    
    return (successful, failed)


async def recalculate_all_metrics(
    db: AsyncSession,
    box_id: UUID = None,
    target_date: date = None
) -> None:
    """
    Main recalculation function
    
    Args:
        db: Database session
        box_id: Optional box UUID to limit recalculation
        target_date: Optional date to limit recalculation
    """
    if box_id and target_date:
        # Recalculate for specific box and date
        print(f"🔄 Recalculating metrics for box {box_id} on {target_date}...")
        await recalculate_metrics_for_box_and_date(db, box_id, target_date)
        return
    
    if box_id:
        # Recalculate for specific box, all dates
        print(f"🔄 Recalculating all metrics for box {box_id}...")
        successful, failed = await recalculate_all_metrics_for_box(db, box_id)
        print(f"\n✅ Recalculated {successful} dates, {failed} failed")
        return
    
    if target_date:
        # Recalculate for specific date, all boxes
        print(f"🔄 Recalculating metrics for all boxes on {target_date}...")
        
        # Get all boxes
        result = await db.execute(select(BoosterBox.id))
        box_ids = [row[0] for row in result.all()]
        
        successful = 0
        failed = 0
        
        for bid in box_ids:
            success = await recalculate_metrics_for_box_and_date(db, bid, target_date)
            if success:
                successful += 1
            else:
                failed += 1
        
        print(f"\n✅ Recalculated {successful} boxes, {failed} failed")
        return
    
    # Recalculate for all boxes, all dates
    print("🔄 Recalculating all metrics for all boxes...")
    
    # Get all unique box IDs with metrics
    result = await db.execute(
        select(distinct(UnifiedBoxMetrics.booster_box_id))
    )
    box_ids = [row[0] for row in result.all()]
    
    if not box_ids:
        print("⚠️  No metrics found in database")
        return
    
    print(f"📦 Found {len(box_ids)} boxes with metrics\n")
    
    total_successful = 0
    total_failed = 0
    
    for i, bid in enumerate(box_ids, 1):
        # Get box name for display
        box_result = await db.execute(
            select(BoosterBox.product_name).where(BoosterBox.id == bid)
        )
        box_name = box_result.scalar() or str(bid)
        
        print(f"[{i}/{len(box_ids)}] Processing {box_name}...")
        
        successful, failed = await recalculate_all_metrics_for_box(db, bid)
        total_successful += successful
        total_failed += failed
    
    print(f"\n{'='*60}")
    print(f"✅ Total: {total_successful} successful, {total_failed} failed")
    print(f"{'='*60}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recalculate unified metrics for historical data"
    )
    parser.add_argument(
        "--box-id",
        type=str,
        help="UUID of specific box to recalculate"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to recalculate (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Recalculate all boxes and dates (default if no filters)"
    )
    
    args = parser.parse_args()
    
    # Parse arguments
    box_id = None
    if args.box_id:
        try:
            box_id = UUID(args.box_id)
        except ValueError:
            print(f"❌ Invalid box UUID: {args.box_id}")
            sys.exit(1)
    
    target_date = None
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Create database connection
    from app.database import create_async_engine, async_sessionmaker
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            await recalculate_all_metrics(db, box_id=box_id, target_date=target_date)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

