#!/usr/bin/env python3
"""
Daily TCGplayer Sales Data Refresh Script

Runs in multiple phases:
1. Apify API - Fetches sales data from TCGplayer via Apify
1b. eBay Scraper - Fetches eBay sales data via 130point.com
2. Listings Scraper - Scrapes active listings count from TCGplayer
3. Rolling Metrics - Computes derived metrics and upserts to DB

Schedule: cron at 10pm EST (03:00 UTC next day). Script adds a random 0–30 min delay
so the actual run happens at a random time within the 10pm window (captures full day's sales).

Run manually (immediate): python scripts/daily_refresh.py --no-delay
Run via cron (10pm EST): schedule "0 3 * * *" (or "0 2 * * *" during EDT)
"""

import sys
import os
import asyncio
import random
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
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


async def run_listings_scraper(debug_box_id: str = None):
    """Run the listings scraper to get active listings count"""
    logger.info("=" * 50)
    logger.info("Starting Phase 2: Listings Scraper...")
    logger.info("=" * 50)

    try:
        from scripts.listings_scraper import run_scraper

        results, errors = await run_scraper(debug_box_id=debug_box_id)
        
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

    # Parse --debug <box_id> if present
    debug_box_id = None
    if "--debug" in sys.argv:
        idx = sys.argv.index("--debug")
        if idx + 1 < len(sys.argv):
            debug_box_id = sys.argv[idx + 1]
            logger.info(f"Debug mode: will only scrape box {debug_box_id}")

    # Random delay (0–30 min) when run by cron so actual work happens at a random time within the 1pm window
    skip_delay = "--no-delay" in sys.argv
    if not skip_delay:
        delay_min, delay_max = 0, 30  # minutes (cron fires at 10pm EST; jitter keeps hit time variable)
        delay_sec = random.randint(delay_min * 60, delay_max * 60)
        eta = datetime.now() + timedelta(seconds=delay_sec)
        logger.info(f"🎲 Random delay: sleeping {delay_sec // 60} min (work will start ~{eta.strftime('%H:%M')} local)")
        time.sleep(delay_sec)
        logger.info("✅ Delay complete, starting Apify + Scraper now.")
        start_time = datetime.now()  # treat real work start as start_time for duration

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
        
        # Send alert
        try:
            from app.services.alert_service import alert_cron_failure
            alert_cron_failure("daily-refresh", str(e), "Apify")
        except Exception as alert_err:
            logger.warning(f"Failed to send alert: {alert_err}")
        
        save_completion_status(status)
        return 1
    
    # Phase 1b: eBay via 130point (non-fatal — failure does NOT block pipeline)
    skip_ebay = os.environ.get("SKIP_EBAY", "").lower() in ("1", "true", "yes")
    status["ebay"] = {"completed": False, "error": None, "skipped": False}
    if skip_ebay:
        logger.info("")
        logger.info("=" * 50)
        logger.info("Phase 1b: eBay Scraper SKIPPED (SKIP_EBAY=1)")
        logger.info("=" * 50)
        status["ebay"]["skipped"] = True
        status["ebay"]["completed"] = True
    else:
        logger.info("")
        logger.info("=" * 50)
        logger.info("Phase 1b: eBay Scraper via 130point.com")
        logger.info("=" * 50)
        try:
            from scripts.ebay_scraper import run_ebay_scraper
            ebay_result = asyncio.run(run_ebay_scraper())
            status["ebay"]["success_count"] = ebay_result.get("results", 0)
            status["ebay"]["error_count"] = len(ebay_result.get("errors", []))
            status["ebay"]["completed"] = True
            logger.info(f"✅ Phase 1b complete: {ebay_result.get('results', 0)} boxes, {len(ebay_result.get('errors', []))} errors")
        except Exception as e:
            status["ebay"]["error"] = str(e)
            logger.warning(f"⚠️  Phase 1b (eBay) failed (non-fatal): {e}")
            import traceback
            logger.warning(traceback.format_exc())

    # Phase 2: Listings Scraper (skip if SKIP_SCRAPER=1 to stay under 512Mi on Render free cron)
    skip_scraper = os.environ.get("SKIP_SCRAPER", "").lower() in ("1", "true", "yes")
    if skip_scraper:
        logger.info("")
        logger.info("=" * 50)
        logger.info("Phase 2: Listings Scraper SKIPPED (SKIP_SCRAPER=1)")
        logger.info("=" * 50)
        scraper_success = 0
        scraper_errors = 0
        status["scraper"]["completed"] = True
        status["scraper"]["skipped"] = True
    else:
        logger.info("")
        logger.info("=" * 50)
        logger.info("Phase 2: Listings Scraper - Fetching Active Listings")
        logger.info("=" * 50)
        
        scraper_success = 0
        scraper_errors = 0
        try:
            scraper_success, scraper_errors = asyncio.run(run_listings_scraper(debug_box_id=debug_box_id))
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
            
            # Send alert
            try:
                from app.services.alert_service import alert_cron_failure
                alert_cron_failure("daily-refresh", str(e), "Scraper")
            except Exception as alert_err:
                logger.warning(f"Failed to send alert: {alert_err}")
            
            save_completion_status(status)
            return 1
    
    # Phase 3: Rolling Metrics (non-fatal — raw data from Phase 1+2 is already saved)
    logger.info("")
    logger.info("=" * 50)
    logger.info("Phase 3: Rolling Metrics — Computing Derived Metrics")
    logger.info("=" * 50)
    status["rolling_metrics"] = {"completed": False, "error": None}
    try:
        from scripts.rolling_metrics import compute_rolling_metrics

        today_str = datetime.now().strftime("%Y-%m-%d")
        rm_result = compute_rolling_metrics(target_date=today_str)
        status["rolling_metrics"]["completed"] = True
        status["rolling_metrics"]["boxes_updated"] = rm_result.get("boxes_updated", 0)
        status["rolling_metrics"]["db_updated"] = rm_result.get("db_updated", 0)
        logger.info(f"✅ Phase 3 complete: {rm_result.get('boxes_updated', 0)} boxes, {rm_result.get('db_updated', 0)} DB rows")
    except Exception as e:
        status["rolling_metrics"]["error"] = str(e)
        logger.warning(f"⚠️  Phase 3 (Rolling Metrics) failed (non-fatal): {e}")
        import traceback
        logger.warning(traceback.format_exc())

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
    logger.info(f"Scraper: {scraper_success} success, {scraper_errors} errors" + (" (skipped)" if skip_scraper else ""))
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

    # Invalidate API caches so leaderboard and box detail serve fresh data immediately
    backend_url = os.environ.get("BACKEND_URL", "").rstrip("/")
    invalidate_secret = os.environ.get("INVALIDATE_CACHE_SECRET", "")
    if backend_url and invalidate_secret:
        try:
            import urllib.request
            url = f"{backend_url}/admin/invalidate-cache"
            logger.info(f"Calling POST {url} to invalidate caches...")
            req = urllib.request.Request(
                url,
                method="POST",
                headers={"X-Invalidate-Secret": invalidate_secret},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode() if hasattr(resp, "read") else ""
                if resp.status in (200, 201):
                    logger.info("✅ API caches invalidated – leaderboard and box detail will serve fresh data")
                else:
                    logger.warning(f"Invalidate cache returned status {resp.status}: {body[:200]}")
        except Exception as e:
            err_code = getattr(e, "code", None)
            err_body = getattr(e, "read", lambda: None)()
            if err_code is not None:
                logger.warning(f"Invalidate cache failed: HTTP {err_code} – check BACKEND_URL and INVALIDATE_CACHE_SECRET match your deployed backend. Body: {(err_body.decode() if err_body else '')[:200]}")
            else:
                logger.warning(f"Could not invalidate API cache: {e}")
    else:
        if not backend_url:
            logger.warning("BACKEND_URL not set – leaderboard/box detail will not auto-update until cache TTL expires; set BACKEND_URL secret (your deployed API URL).")
        if not invalidate_secret:
            logger.warning("INVALIDATE_CACHE_SECRET not set – leaderboard/box detail will not auto-update until cache TTL expires; set INVALIDATE_CACHE_SECRET secret (same value as on your backend).")
    
    # Optional success alert (only if ALERT_ON_SUCCESS=true)
    if not status["overall_success"]:
        try:
            from app.services.alert_service import alert_cron_failure
            error_msg = f"Apify errors: {status['apify']['error_count']}, Scraper errors: {status['scraper']['error_count']}"
            alert_cron_failure("daily-refresh", error_msg, "Overall")
        except Exception as alert_err:
            logger.warning(f"Failed to send alert: {alert_err}")
    else:
        try:
            from app.services.alert_service import alert_cron_success
            summary = f"Apify: {status['apify']['success_count']} boxes, Scraper: {status['scraper']['success_count']} boxes"
            alert_cron_success("daily-refresh", duration, summary)
        except Exception as alert_err:
            logger.warning(f"Failed to send success alert: {alert_err}")
    
    logger.info("")
    logger.info("📊 Check status file: logs/daily_refresh_status.json")
    logger.info("📋 Check full log: logs/daily_refresh.log")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


