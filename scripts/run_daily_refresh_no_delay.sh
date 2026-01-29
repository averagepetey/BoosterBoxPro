#!/usr/bin/env bash
# Run daily refresh locally with no delay. Ensures deps + Playwright, loads .env, runs script.
set -e
cd "$(dirname "$0")/.."
echo "Installing dependencies if needed..."
pip3 install --no-cache-dir -q -r requirements.txt
echo "Ensuring Playwright Chromium..."
playwright install chromium 2>/dev/null || true
echo "Loading .env and running daily_refresh.py --no-delay..."
set -a
[ -f .env ] && source .env
set +a
python3 scripts/daily_refresh.py --no-delay
