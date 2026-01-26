#!/usr/bin/env python3
"""
Quick script to check the status of the last daily refresh run.
Usage: python scripts/check_daily_refresh_status.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
status_file = project_root / "logs" / "daily_refresh_status.json"

if not status_file.exists():
    print("❌ No status file found. The daily refresh hasn't run yet.")
    sys.exit(1)

with open(status_file, 'r') as f:
    status = json.load(f)

print("=" * 60)
print("📊 Daily Refresh Status")
print("=" * 60)

# Overall status
if status["status"] == "completed":
    if status["overall_success"]:
        print("✅ Status: COMPLETED SUCCESSFULLY")
    else:
        print("⚠️  Status: COMPLETED WITH ERRORS")
elif status["status"] == "running":
    print("🔄 Status: CURRENTLY RUNNING")
else:
    print(f"❌ Status: {status['status'].upper()}")

print()

# Timing
if status.get("start_time"):
    start = datetime.fromisoformat(status["start_time"])
    print(f"⏰ Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")

if status.get("end_time"):
    end = datetime.fromisoformat(status["end_time"])
    print(f"⏰ Ended: {end.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if status.get("duration_seconds"):
        duration = status["duration_seconds"]
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")

print()

# Phase 1: Apify
print("Phase 1: Apify API")
if status["apify"]["completed"]:
    print(f"  ✅ Completed: {status['apify']['success_count']} success, {status['apify']['error_count']} errors")
    if status["apify"].get("error"):
        print(f"  ❌ Error: {status['apify']['error']}")
else:
    print("  ⏳ Not completed")
    if status["apify"].get("error"):
        print(f"  ❌ Error: {status['apify']['error']}")

print()

# Phase 2: Scraper
print("Phase 2: Listings Scraper")
if status["scraper"]["completed"]:
    print(f"  ✅ Completed: {status['scraper']['success_count']} success, {status['scraper']['error_count']} errors")
    if status["scraper"].get("error"):
        print(f"  ❌ Error: {status['scraper']['error']}")
else:
    print("  ⏳ Not completed")
    if status["scraper"].get("error"):
        print(f"  ❌ Error: {status['scraper']['error']}")

print()
print("=" * 60)
print(f"📋 Full log: logs/daily_refresh.log")
print("=" * 60)
