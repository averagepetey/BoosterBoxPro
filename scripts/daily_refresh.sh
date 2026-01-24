#!/bin/bash
# Daily TCGplayer Sales Data Refresh
# Run this via cron: 0 9 * * * /path/to/daily_refresh.sh

PROJECT_DIR="/Users/johnpetersenhomefolder/Desktop/Vibe Code Bin/BoosterBoxPro"
LOG_FILE="$PROJECT_DIR/logs/daily_refresh.log"
API_KEY="your-secret-api-key-here"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "========================================" >> "$LOG_FILE"
echo "$(date): Starting daily refresh..." >> "$LOG_FILE"

# Call the API endpoint
RESPONSE=$(curl -s -X POST "http://localhost:8000/admin/refresh-sales-data" \
  -H "X-Admin-Api-Key: $API_KEY" \
  2>&1)

echo "Response: $RESPONSE" >> "$LOG_FILE"
echo "$(date): Refresh complete" >> "$LOG_FILE"


