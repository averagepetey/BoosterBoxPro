#!/usr/bin/env python3
"""
Daily TCGplayer Sales Data Refresh Script

Runs in two phases:
1. Apify API - Fetches sales data from TCGplayer via Apify
2. Listings Scraper - Scrapes active listings count from TCGplayer

Run manually: python scripts/daily_refresh.py
Run via cron (12pm daily): 0 12 * * * cd /path/to/project && venv/bin/python scripts/daily_refresh.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
import json
import logging

# Setup logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "daily_refresh.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_listings_scraper():
    """Run the listings scraper to get active listings count"""
    logger.info("=" * 50)
    logger.info("Starting Phase 2: Listings Scraper...")
    logger.info("=" * 50)
    
    try:
        from scripts.listings_scraper import run_scraper
        
        results, errors = await run_scraper()
        
        logger.info(f"✅ Scraper Success: {len(results)} boxes")
        logger.info(f"❌ Scraper Errors: {len(errors)} boxes")
        
        if errors:
            logger.warning(f"Failed boxes: {errors}")
        
        return len(results), len(errors)
        
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0, 0


def save_completion_status(status_data: dict):
    """Save completion status to a JSON file for easy checking"""
    status_file = project_root / "logs" / "daily_refresh_status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2, default=str)
    logger.info(f"📊 Status saved to: {status_file}")


def main():
    start_time = datetime.now()
    logger.info("=" * 70)
    logger.info("Starting daily TCGplayer refresh (Apify + Scraper)")
    logger.info(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    status = {
        "status": "running",
        "start_time": start_time.isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "apify": {
            "success_count": 0,
            "error_count": 0,
            "completed": False,
            "error": None
        },
        "scraper": {
            "success_count": 0,
            "error_count": 0,
            "completed": False,
            "error": None
        },
        "overall_success": False
    }
    
    # Phase 1: Apify API
    logger.info("")
    logger.info("=" * 50)
    logger.info("Phase 1: Apify API - Fetching Sales Data")
    logger.info("=" * 50)
    
    apify_result = None
    try:
        from app.services.tcgplayer_apify import refresh_all_boxes_sales_data
        
        apify_result = refresh_all_boxes_sales_data()
        
        status["apify"]["success_count"] = apify_result['success_count']
        status["apify"]["error_count"] = apify_result['error_count']
        status["apify"]["completed"] = True
        
        logger.info(f"✅ Apify Success: {apify_result['success_count']} boxes")
        logger.info(f"❌ Apify Errors: {apify_result['error_count']} boxes")
        logger.info(f"📅 Date: {apify_result['date']}")
        
        # Log top 5
        logger.info("Top 5 by Volume:")
        for box in apify_result.get('top_5_by_volume', []):
            change = box.get('change_pct')
            change_str = f" ({change:+.1f}%)" if change else ""
            logger.info(f"  - {box['name']}: ${box['daily_volume']:.2f}/day{change_str}")
        
        # Log alerts
        if apify_result.get('alerts'):
            logger.warning("🚨 ALERTS:")
            for alert in apify_result['alerts']:
                logger.warning(f"  - {alert['box']}: {alert['type']} ({alert['change_pct']:+.1f}%)")
        
        logger.info("")
        logger.info("✅ Phase 1 (Apify) complete!")
        
    except Exception as e:
        status["apify"]["error"] = str(e)
        logger.error(f"Apify phase failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        save_completion_status(status)
        return 1
    
    # Phase 2: Listings Scraper
    logger.info("")
    logger.info("=" * 50)
    logger.info("Phase 2: Listings Scraper - Fetching Active Listings")
    logger.info("=" * 50)
    
    scraper_success = 0
    scraper_errors = 0
    try:
        scraper_success, scraper_errors = asyncio.run(run_listings_scraper())
        status["scraper"]["success_count"] = scraper_success
        status["scraper"]["error_count"] = scraper_errors
        status["scraper"]["completed"] = True
        
        logger.info("")
        logger.info("✅ Phase 2 (Scraper) complete!")
        
    except Exception as e:
        status["scraper"]["error"] = str(e)
        logger.error(f"Scraper phase failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        save_completion_status(status)
        return 1
    
    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("Daily Refresh Complete!")
    logger.info("=" * 70)
    logger.info(f"⏰ Start: {start_time.strftime('%H:%M:%S')}")
    logger.info(f"⏰ End: {end_time.strftime('%H:%M:%S')}")
    logger.info(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info(f"Apify: {apify_result['success_count']} success, {apify_result['error_count']} errors")
    logger.info(f"Scraper: {scraper_success} success, {scraper_errors} errors")
    logger.info("=" * 70)
    
    # Update status
    status["status"] = "completed"
    status["end_time"] = end_time.isoformat()
    status["duration_seconds"] = duration
    status["overall_success"] = (
        status["apify"]["completed"] and 
        status["scraper"]["completed"] and
        status["apify"]["error_count"] == 0
    )
    
    save_completion_status(status)
    
    logger.info("")
    logger.info("📊 Check status file: logs/daily_refresh_status.json")
    logger.info("📋 Check full log: logs/daily_refresh.log")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


