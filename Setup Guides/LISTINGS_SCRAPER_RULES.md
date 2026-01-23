# Listings Scraper - Complete Rules & Specifications

> **Reference Document:** If the AI forgets these rules, tell it to read this file.

---

## Overview

A gentle, stealth web scraper to extract active listings data from TCGplayer for 18 One Piece booster boxes. Runs daily alongside Apify (which provides sales data).

---

## Data Sources

| Data | Source | Cost |
|------|--------|------|
| Sales per day | Apify API | ~$13/month |
| Market price | Apify API | included |
| Daily volume | Apify API | included |
| **Active listings count** | **This scraper** | **Free** |
| **Floor price (backup)** | **This scraper** | **Free** |
| **Listings within 20%** | **This scraper** | **Free** |

---

## Schedule

| Task | Time | Randomization |
|------|------|---------------|
| Apify refresh | 12:00 PM | ± 30 minutes |
| Listings scraper | 12:00 PM | ± 45 minutes |

Both run around the same time so data is synchronized.

---

## Target Products

18 core One Piece booster boxes:

```
OP-01 Romance Dawn (Blue)
OP-01 Romance Dawn (White)
OP-02 Paramount War
OP-03 Pillars of Strength
OP-04 Kingdoms of Intrigue
OP-05 Awakening of the New Era
OP-06 Wings of the Captain
OP-07 500 Years in the Future
OP-08 Two Legends
OP-09 Emperors in the New World
OP-10 Royal Blood
OP-11 A Fist of Divine Speed
OP-12 Legacy of the Master
OP-13 Carrying on His Will
EB-01 Memorial Collection
EB-02 Anime 25th Collection
PRB-01 Premium Booster
PRB-02 Premium Booster Vol. 2
```

---

## Stealth Rules

### Browser Configuration

| Setting | Value | Reason |
|---------|-------|--------|
| Browser | Real Chrome (`channel="chrome"`) | Real TLS fingerprint |
| Mode | Headed (minimized) | Perfect font/canvas fingerprint |
| Stealth plugin | `playwright-stealth` | Patches JS detections |
| User-Agent | Single consistent UA per session | Same IP + different UAs = suspicious |
| Viewport | Random realistic (1920x1080, 1440x900, etc.) | Match UA platform |

### Request Behavior

| Setting | Value | Reason |
|---------|-------|--------|
| Delay between pages | 5-15 seconds (normal distribution, mean=8s) | Human-like timing |
| Delay between boxes | 5-15 seconds | Avoid bursts |
| Request order | **Random shuffle** | Sequential = bot pattern |
| First page | Visit TCGplayer homepage | Natural navigation |
| Cookie banner | **Do NOT interact** | Clicking daily = suspicious |
| Session | Fresh each run (no persistent cookies) | Privacy-user behavior |

### Noise Products

| Setting | Value |
|---------|-------|
| Noise count | **Random 2-8 products per day** |
| Noise pool | 30+ random sealed products (Pokemon, MTG, Yu-Gi-Oh, OP starters) |
| Purpose | Mask the pattern of always visiting same 18 products |

**Daily pattern example:**
```
Day 1: 18 targets + 6 noise = 24 products (random order)
Day 2: 18 targets + 3 noise = 21 products (random order)
Day 3: 18 targets + 8 noise = 26 products (random order)
```

### Pagination

| Setting | Value |
|---------|-------|
| Strategy | Paginate until price exceeds floor + 20% |
| Average pages | ~3-4 per box |
| Max pages | Stop when listing price > threshold |

---

## Data Filtering Rules

### Rule 1: Exclude Japanese Listings

**Check for these keywords in title, description, condition, or variant:**

```python
JAPANESE_INDICATORS = [
    'japanese', 'japan', 'jp version', 'jp ver',
    '日本', '日本語', 'japanese language',
    'asian english', 'asia', 'asian'
]
```

**Also check seller location** if available - exclude sellers from Japan.

### Rule 2: Exclude Suspicious/Damaged Listings

**Filter listings containing these keywords:**

```python
SUSPICIOUS_KEYWORDS = [
    'damaged', 'opened', 'no shrink', 'loose',
    'played', 'heavy play', 'poor condition',
    'missing', 'incomplete', 'resealed',
    'no seal', 'unsealed', 'box only',
    'empty', 'display', 'for display'
]
```

### Rule 3: Outlier Price Detection

**Threshold:** Listings priced < 75% of market price are suspicious.

**Logic:**
```
IF market_price = $550:
   outlier_threshold = $550 × 0.75 = $412.50
   
   Listings below $412.50:
   - IF 1-4 clean listings → FILTER as outliers
   - IF 5+ clean listings → KEEP as legitimate pullback
```

**"Clean" means:** No suspicious keywords in description.

**Example - Filter (outliers):**
```
Market: $550
$400 - "Sealed NM" (clean)
$405 - "Sealed NM" (clean)  
$380 - "Japanese" (filtered - Japanese)

Clean low-priced: 2 (< 5)
Decision: FILTER both
```

**Example - Keep (real pullback):**
```
Market: $550
$400 - "Sealed NM" (clean)
$405 - "Sealed NM" (clean)
$408 - "Sealed NM" (clean)
$410 - "Sealed NM" (clean)
$412 - "Sealed NM" (clean)

Clean low-priced: 5 (≥ 5)
Decision: KEEP all (legitimate market pullback)
```

### Rule 4: Within 20% Calculation

After all filtering, count listings where:
```
price <= floor_price × 1.20
```

**Example:**
```
Floor price: $555
Threshold: $555 × 1.20 = $666
Count listings from $555 to $666
```

---

## Filter Pipeline (Order of Operations)

```python
def process_listings(raw_listings, market_price):
    # Step 1: Remove Japanese listings
    listings = filter_japanese(raw_listings)
    
    # Step 2: Remove suspicious/damaged listings  
    listings = filter_suspicious(listings)
    
    # Step 3: Smart outlier detection (75% rule with 5+ cluster)
    listings = filter_outliers(listings, market_price, min_cluster=5)
    
    # Step 4: Calculate floor price (lowest remaining)
    floor_price = min(l['price'] for l in listings)
    
    # Step 5: Count within 20% of floor
    threshold = floor_price * 1.20
    within_20pct = [l for l in listings if l['price'] <= threshold]
    
    return {
        'total_listings': len(listings),
        'floor_price': floor_price,
        'listings_within_20pct': len(within_20pct),
        'all_listings': listings
    }
```

---

## Configuration Constants

```python
# Timing
SCRAPE_TIME_BASE = "12:00"  # Noon
SCRAPE_TIME_VARIANCE = 45   # ± 45 minutes

# Stealth
DELAY_MIN = 5               # seconds
DELAY_MAX = 15              # seconds
DELAY_MEAN = 8              # seconds (normal distribution)
NOISE_MIN = 2               # minimum noise products
NOISE_MAX = 8               # maximum noise products

# Filtering
OUTLIER_THRESHOLD_PCT = 0.75    # 75% of market price
MIN_CLUSTER_SIZE = 5            # Need 5+ clean low-priced to confirm pullback
WITHIN_20PCT_THRESHOLD = 1.20   # Floor × 1.20

# Browser
BROWSER_CHANNEL = "chrome"      # Use real Chrome
HEADLESS = False                # Headed mode (minimized)
USE_STEALTH = True              # playwright-stealth plugin
```

---

## Output Data Format

Each box entry in `historical_entries.json`:

```json
{
  "date": "2026-01-23",
  "source": "tcgplayer_scraper",
  "floor_price_usd": 555.00,
  "total_listings": 127,
  "listings_within_20pct": 49,
  "market_price_usd": 551.27,
  "scrape_timestamp": "2026-01-23T12:15:32",
  "filters_applied": {
    "japanese_removed": 3,
    "suspicious_removed": 2,
    "outliers_removed": 1
  }
}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| 403 Forbidden | Stop immediately, log, alert |
| 429 Rate Limited | Stop, wait 1 hour, don't retry today |
| CAPTCHA | Stop, log, alert (manual intervention) |
| Timeout | Skip box, continue with others |
| HTML changed | Log error, alert, continue |
| 0 listings found | Log warning, might be delisted |

---

## Alerts

Send alert (Discord/email) when:
- Scraper fails completely
- More than 3 boxes fail
- Detected CAPTCHA or 403
- Listings drop >50% suddenly (anomaly)

---

## Request Estimates

| Scenario | Products | Pages | Total Requests |
|----------|----------|-------|----------------|
| Minimum | 20 (18+2) | ~80 | ~80 |
| Average | 23 (18+5) | ~92 | ~92 |
| Maximum | 26 (18+8) | ~104 | ~104 |

**Runtime:** ~15-25 minutes per day

---

## Detection Risk Assessment

| Timeframe | Risk | Notes |
|-----------|------|-------|
| Week 1-4 | 🟢 Very Low | Looks like collector browsing |
| Month 1-3 | 🟢 Low | Pattern emerging but not flagged |
| Month 6+ | 🟡 Low-Medium | Clear pattern if they analyze |

**If detected:**
- 80% chance: IP block (use VPN to continue)
- 15% chance: CAPTCHA wall
- 5% chance: Rate limited
- <0.1% chance: Legal action

---

## Checklist Before Running

```
☐ Playwright installed
☐ playwright-stealth installed
☐ Real Chrome available (channel="chrome")
☐ 30+ noise products configured
☐ All 18 TCGplayer URLs verified
☐ Market price available (from Apify)
☐ Cron job configured for 12 PM
☐ Alert webhook configured (Discord/email)
☐ Test run on single box successful
```

---

## Files

```
scripts/
├── listings_scraper.py       # Main scraper
├── listings_scraper_test.py  # Test single box
└── run_listings_scraper.sh   # Cron wrapper

data/
├── historical_entries.json   # Updated with listings data
└── scraper_cookies.json      # NOT USED (fresh sessions)

logs/
└── scraper_YYYY-MM-DD.log    # Daily logs
```

---

## Quick Reference Commands

```bash
# Test single box
python scripts/listings_scraper_test.py

# Run full scraper manually
python scripts/listings_scraper.py

# Check cron jobs
crontab -l

# View today's log
cat logs/scraper_$(date +%Y-%m-%d).log
```

---

*Last updated: 2026-01-23*


