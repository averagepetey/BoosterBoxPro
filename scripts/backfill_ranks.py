#!/usr/bin/env python3
"""
Backfill Historical Ranks Script
Calculates and updates ranks for all historical data

Usage:
    python scripts/backfill_ranks.py [--date <YYYY-MM-DD>] [--all]
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings
from app.services.ranking_calculator import RankingCalculator
from app.models.unified_box_metrics import UnifiedBoxMetrics


async def backfill_ranks_for_date(
    db: AsyncSession,
    target_date: date
) -> tuple[int, int]:
    """
    Backfill ranks for a specific date
    
    Returns:
        Tuple of (successful_count, failed_count)
    """
    calculator = RankingCalculator(db)
    
    try:
        updated_count = await calculator.update_ranks_for_date(target_date)
        print(f"  ✅ Updated {updated_count} boxes for {target_date}")
        return (updated_count, 0)
    except Exception as e:
        print(f"  ❌ Error updating ranks for {target_date}: {e}")
        return (0, 1)


async def backfill_all_ranks(db: AsyncSession) -> None:
    """
    Backfill ranks for all dates with metrics but no ranks
    """
    # Get all unique dates with metrics
    result = await db.execute(
        select(distinct(UnifiedBoxMetrics.metric_date))
        .order_by(UnifiedBoxMetrics.metric_date.asc())
    )
    
    dates = [row[0] for row in result.all()]
    
    if not dates:
        print("⚠️  No metrics found in database")
        return
    
    print(f"📊 Found {len(dates)} dates with metrics\n")
    
    total_successful = 0
    total_failed = 0
    
    for i, target_date in enumerate(dates, 1):
        print(f"[{i}/{len(dates)}] Processing {target_date}...")
        
        successful, failed = await backfill_ranks_for_date(db, target_date)
        total_successful += successful
        total_failed += failed
    
    print(f"\n{'='*60}")
    print(f"✅ Total: {total_successful} boxes updated, {total_failed} errors")
    print(f"{'='*60}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Backfill historical ranks for all dates with metrics"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to backfill (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Backfill all dates (default if no filters)"
    )
    
    args = parser.parse_args()
    
    # Parse date if provided
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
            if target_date:
                print(f"🔄 Backfilling ranks for {target_date}...")
                await backfill_ranks_for_date(db, target_date)
            else:
                await backfill_all_ranks(db)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

