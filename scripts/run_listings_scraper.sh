#!/bin/bash
# run_listings_scraper.sh
# Cron wrapper for listings scraper with random delay

set -e

cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro

LOG_FILE="logs/scraper_cron_$(date +%Y-%m-%d).log"

echo "========================================" >> "$LOG_FILE"
echo "Cron started at: $(date)" >> "$LOG_FILE"

# Random delay: 0-90 minutes
RANDOM_DELAY=$((RANDOM % 90))
echo "Random delay: ${RANDOM_DELAY} minutes" >> "$LOG_FILE"
sleep $((RANDOM_DELAY * 60))

echo "Starting scraper at: $(date)" >> "$LOG_FILE"

source venv/bin/activate
python scripts/listings_scraper.py >> "$LOG_FILE" 2>&1

echo "Scraper finished at: $(date)" >> "$LOG_FILE"
deactivate
