#!/usr/bin/env python3
"""
Daily TCGplayer Sales Data Refresh Script

Run manually: python scripts/daily_refresh.py
Run via cron: 0 9 * * * cd /path/to/project && venv/bin/python scripts/daily_refresh.py
"""

import sys
import os
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


def main():
    logger.info("=" * 50)
    logger.info("Starting daily TCGplayer refresh...")
    
    try:
        from app.services.tcgplayer_apify import refresh_all_boxes_sales_data
        
        result = refresh_all_boxes_sales_data()
        
        logger.info(f"✅ Success: {result['success_count']} boxes")
        logger.info(f"❌ Errors: {result['error_count']}")
        logger.info(f"📅 Date: {result['date']}")
        
        # Log top 5
        logger.info("Top 5 by Volume:")
        for box in result.get('top_5_by_volume', []):
            change = box.get('change_pct')
            change_str = f" ({change:+.1f}%)" if change else ""
            logger.info(f"  - {box['name']}: ${box['daily_volume']:.2f}/day{change_str}")
        
        # Log alerts
        if result.get('alerts'):
            logger.warning("🚨 ALERTS:")
            for alert in result['alerts']:
                logger.warning(f"  - {alert['box']}: {alert['type']} ({alert['change_pct']:+.1f}%)")
        
        logger.info("Refresh complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


