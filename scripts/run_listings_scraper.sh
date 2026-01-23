#!/bin/bash
# run_listings_scraper.sh
# Cron wrapper for listings scraper with random delay
#
# Add to crontab with: crontab -e
# Run at 11:15 AM daily (scraper adds random delay up to 90 min):
# 15 11 * * * /path/to/BoosterBoxPro/scripts/run_listings_scraper.sh

set -e

# Navigate to project root
cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro

# Log file
LOG_FILE="logs/scraper_cron_$(date +%Y-%m-%d).log"

echo "========================================" >> "$LOG_FILE"
echo "Cron started at: $(date)" >> "$LOG_FILE"

# Random delay: 0-90 minutes (to hit 11:15 AM - 12:45 PM window)
RANDOM_DELAY=$((RANDOM % 90))
echo "Random delay: ${RANDOM_DELAY} minutes" >> "$LOG_FILE"
sleep $((RANDOM_DELAY * 60))

echo "Starting scraper at: $(date)" >> "$LOG_FILE"

# Activate virtual environment
source venv/bin/activate

# Run scraper
python scripts/listings_scraper.py >> "$LOG_FILE" 2>&1

echo "Scraper finished at: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Deactivate
deactivate


