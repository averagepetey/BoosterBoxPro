# Monthly Data Entry Guide

This guide explains how to input a year of monthly snapshots of booster box data into the system.

## How It Works

The system can process multiple monthly snapshots with specified dates. Each screenshot is:
1. Processed to extract data
2. Stored with the specified date
3. Used to calculate historical metrics
4. Tracked to prevent duplicates

## Method 1: Send Screenshots One at a Time with Dates

When you send a screenshot, you can specify the date in your message:

**Format:**
```
[Send screenshot] + "Date: 2024-01-15" or "January 2024" or "2024-01"
```

**Examples:**
- Send screenshot + "This is January 2024 data"
- Send screenshot + "Date: 2024-02-01"
- Send screenshot + "OP-01 data for March 2024"

The system will:
- Extract the date from your message
- Process the screenshot
- Store it with that date
- Calculate metrics using all historical data

## Method 2: Batch Processing (For Multiple Screenshots)

If you have multiple monthly screenshots, you can send them all and I'll process them with dates.

**Just send the screenshots and tell me:**
- "These are monthly snapshots for 2024"
- "Process these 12 screenshots for each month of 2024"
- "These are OP-01 snapshots: January through December 2024"

I'll process each one and assign the appropriate dates.

## Date Formats Accepted

The system accepts dates in various formats:
- `YYYY-MM-DD` (e.g., "2024-01-15")
- `YYYY-MM` (e.g., "2024-01" - will use 1st of month)
- Month names (e.g., "January 2024", "Jan 2024")
- Relative dates (e.g., "3 months ago", "last January")

## What Gets Stored

For each monthly snapshot, the system stores:
- **Date**: The specified date (or 1st of month if only month/year given)
- **Raw Data**: All extracted metrics (floor price, volume, sales, listings, etc.)
- **Data Type**: Sales, listings, or combined
- **Source**: Screenshot metadata
- **Historical Context**: Links to previous months

## Metric Calculations

With monthly data, the system calculates:
- **Trends**: Price changes month-over-month
- **Averages**: 30-day, 90-day, and yearly averages
- **Projections**: Based on historical patterns
- **Comparisons**: Current vs historical performance

## Example Workflow

**You:** "I have 12 monthly snapshots for OP-01 from 2024"

**Me:** "Great! Send them one at a time, and I'll process each with the appropriate date. You can specify the month in your message, or I can assign them sequentially."

**You:** [Sends January screenshot] "January 2024"

**System:**
- Extracts data from screenshot
- Stores with date: 2024-01-01
- Calculates metrics
- Reports: "✅ January 2024 data processed for OP-01"

**You:** [Sends February screenshot] "February 2024"

**System:**
- Extracts data from screenshot
- Stores with date: 2024-02-01
- Merges with January data
- Calculates updated metrics including trends
- Reports: "✅ February 2024 data processed. Price change: +5.2% from January"

## Tips

1. **Be Specific**: Include the month/year in your message when sending screenshots
2. **Order Matters**: Processing in chronological order helps with trend calculations
3. **Consistency**: Use the same format for dates (e.g., always "YYYY-MM-DD")
4. **Multiple Boxes**: If screenshots are for different boxes, the system will identify them automatically

## What Happens After Processing

Once all monthly snapshots are processed:
- ✅ Complete historical data for the year
- ✅ Accurate trend calculations
- ✅ Month-over-month comparisons
- ✅ Long-term averages and projections
- ✅ All metrics updated in the app

## Ready to Start?

Just send your first monthly screenshot and specify the date! I'll process it and guide you through the rest.



