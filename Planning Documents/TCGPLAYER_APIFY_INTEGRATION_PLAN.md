# TCGplayer Apify Integration Plan

## Overview

Integrating the Apify TCGplayer Sales History actor to automate sales data collection for all 18 One Piece booster boxes.

**Actor:** `scraped/tcgplayer-sales-history`  
**Cost:** $10/month + ~$5-10/month usage  
**Benefit:** Automates ~80% of daily data collection

---

## Step 1: Existing Infrastructure Audit ✅

### What Already Exists

| Component | Status | Location |
|-----------|--------|----------|
| Config placeholders for API keys | ✅ Ready | `app/config.py` (commented) |
| Historical data service | ✅ Ready | `app/services/historical_data.py` |
| Volume calculation service | ✅ Ready | `app/services/volume_calculation.py` |
| Daily snapshot function | ✅ Ready | `calculate_volume_from_daily_snapshots()` |
| UUID mapping (DB ↔ Leaderboard) | ✅ Ready | `DB_TO_LEADERBOARD_UUID_MAP` |
| Data storage (JSON) | ✅ Ready | `data/historical_entries.json` |

### What Needs to Be Built

| Component | Priority | Notes |
|-----------|----------|-------|
| Apify client service | 🔴 High | New service to call Apify API |
| TCGplayer URL mapping | 🔴 High | Map 18 boxes to TCGplayer product URLs |
| Scheduled job runner | 🟡 Medium | Daily automation (can use cron initially) |
| Data transformer | 🔴 High | Convert Apify response → our format |
| Error handling & retry | 🟡 Medium | Handle API failures gracefully |

---

## Step 2: Calculation Consistency

### Current Metrics We Track

| Metric | Current Source | Apify Source | Consistency Plan |
|--------|----------------|--------------|------------------|
| `floor_price_usd` | Screenshot | `lowSalePrice` | Use Apify `lowSalePrice` as floor |
| `boxes_sold_per_day` | Screenshot | `averageDailyQuantitySold` | Direct mapping ✅ |
| `daily_volume_usd` | Calculated | `marketPrice × quantitySold` | Calculate from Apify data |
| `active_listings_count` | Screenshot | ❌ Not available | **Manual screenshots still needed** |
| `boxes_added_today` | Calculated | ❌ Not available | Calculate from day-over-day listings |
| `unified_volume_usd` | 30d × daily | Sum buckets | Sum Apify bucket volumes |

### Calculation Formulas (Apify Data)

```python
# Daily volume from Apify bucket
daily_volume = bucket['marketPrice'] * bucket['quantitySold']

# 30-day volume (sum buckets)
volume_30d = sum(bucket['marketPrice'] * bucket['quantitySold'] for bucket in buckets[-30:])

# Average daily sales (direct from API)
boxes_sold_per_day = data['averageDailyQuantitySold']

# Floor price (from most recent bucket)
floor_price = buckets[-1]['lowSalePrice'] if buckets else data.get('marketPrice')
```

### Data Validation Rules

1. **Price sanity check:** $50 < floor_price < $10,000
2. **Volume sanity check:** daily_volume > 0 if boxes_sold > 0
3. **Sales correlation:** If sales reported, volume must exist
4. **Date continuity:** No gaps > 7 days without flagging

---

## Step 3: Integration Architecture

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Apify API      │────▶│  TCGplayer      │────▶│  Data           │
│  (Daily Cron)   │     │  Scraper        │     │  Transformer    │
└─────────────────┘     │  Service        │     └────────┬────────┘
                        └─────────────────┘              │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  historical_    │◀────│  JSON Storage   │◀────│  Merged Data    │
│  entries.json   │     │  Handler        │     │  (API + Manual) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         ▲
                                                         │
                        ┌─────────────────┐              │
                        │  Manual Entry   │──────────────┘
                        │  (Listings only)│
                        └─────────────────┘
```

### New Files to Create

```
app/
├── services/
│   └── tcgplayer_apify.py    # NEW: Apify client & data transformer
├── jobs/
│   └── daily_sync.py         # NEW: Scheduled job runner
└── config.py                 # UPDATE: Add APIFY_API_TOKEN
```

---

## Step 4: Questions for User

### Critical Questions

1. **TCGplayer URLs**
   - Do you have the exact TCGplayer product URLs for all 18 boxes?
   - Example: `https://www.tcgplayer.com/product/XXXXX/one-piece-...`
   - I can find them, but confirm you don't have a list already.

2. **Apify Account**
   - Have you created an Apify account yet?
   - Do you have an API token ready?

3. **Bucket Granularity**
   - The sample shows weekly buckets. Want me to test with a real OP box URL to confirm if recent data is daily?

4. **Listings Data**
   - Confirm: You'll continue manual screenshots for listings count only?
   - Frequency: Daily? Every few days?

5. **Historical Backfill**
   - Should we backfill historical data from Apify (if available)?
   - Or start fresh from today forward?

6. **Schedule Preference**
   - What time should daily sync run? (Recommend: 2 AM EST, after TCGplayer updates)
   - Want notification on failure?

### Nice-to-Have Questions

7. **Multiple Variants**
   - Some boxes have variants (OP-01 Blue/White). How does TCGplayer list these?
   - Separate product pages or one page with variants?

8. **Error Handling**
   - If Apify fails for a box, should we:
     - a) Use previous day's data
     - b) Skip that box entirely
     - c) Alert you immediately

9. **Data Merge Strategy**
   - If both Apify and manual entry exist for same date:
     - a) Prefer Apify (automated = consistent)
     - b) Prefer manual (human-verified)
     - c) Merge (Apify for sales, manual for listings)

---

## Implementation Phases

### Phase A: Setup (30 min)
- [ ] Add `apify-client` to requirements.txt
- [ ] Add `APIFY_API_TOKEN` to config
- [ ] Create TCGplayer URL mapping

### Phase B: Service Build (1-2 hours)
- [ ] Create `app/services/tcgplayer_apify.py`
- [ ] Implement data transformer
- [ ] Add error handling & validation

### Phase C: Integration (1 hour)
- [ ] Connect to existing historical_data.py
- [ ] Ensure calculations match existing methodology
- [ ] Test with one box (OP-13)

### Phase D: Automation (30 min)
- [ ] Create daily job script
- [ ] Setup cron or scheduler
- [ ] Add logging & monitoring

### Phase E: Validation (ongoing)
- [ ] Compare API data vs manual screenshots
- [ ] Verify calculations match
- [ ] Document any discrepancies

---

## TCGplayer Product URLs (To Fill)

| Set Code | Product Name | TCGplayer URL |
|----------|--------------|---------------|
| OP-01 Blue | Romance Dawn (Blue) | `TBD` |
| OP-01 White | Romance Dawn (White) | `TBD` |
| OP-02 | Paramount War | `TBD` |
| OP-03 | Pillars of Strength | `TBD` |
| OP-04 | Kingdoms of Intrigue | `TBD` |
| OP-05 | Awakening of the New Era | `TBD` |
| OP-06 | Wings of the Captain | `TBD` |
| OP-07 | 500 Years in the Future | `TBD` |
| OP-08 | Two Legends | `TBD` |
| OP-09 | Emperors in the New World | `TBD` |
| OP-10 | Royal Blood | `TBD` |
| OP-11 | A Fist of Divine Speed | `TBD` |
| OP-12 | Legacy of the Master | `TBD` |
| OP-13 | Carrying on His Will | `TBD` |
| EB-01 | Memorial Collection | `TBD` |
| EB-02 | Anime 25th Collection | `TBD` |
| PRB-01 | Premium Booster | `TBD` |
| PRB-02 | Premium Booster Vol. 2 | `TBD` |

---

## Cost Estimate

| Item | Monthly Cost |
|------|--------------|
| Apify Actor Rental | $10.00 |
| API Usage (18 boxes × 30 days) | ~$5-10 |
| **Total** | **~$15-20/month** |

**ROI:** Saves ~2-3 hours/day of manual screenshot work

---

## Next Steps

1. **Answer questions above** (especially #1-6)
2. **Create Apify account** if not done
3. **I'll build the integration** once questions are answered



## Overview

Integrating the Apify TCGplayer Sales History actor to automate sales data collection for all 18 One Piece booster boxes.

**Actor:** `scraped/tcgplayer-sales-history`  
**Cost:** $10/month + ~$5-10/month usage  
**Benefit:** Automates ~80% of daily data collection

---

## Step 1: Existing Infrastructure Audit ✅

### What Already Exists

| Component | Status | Location |
|-----------|--------|----------|
| Config placeholders for API keys | ✅ Ready | `app/config.py` (commented) |
| Historical data service | ✅ Ready | `app/services/historical_data.py` |
| Volume calculation service | ✅ Ready | `app/services/volume_calculation.py` |
| Daily snapshot function | ✅ Ready | `calculate_volume_from_daily_snapshots()` |
| UUID mapping (DB ↔ Leaderboard) | ✅ Ready | `DB_TO_LEADERBOARD_UUID_MAP` |
| Data storage (JSON) | ✅ Ready | `data/historical_entries.json` |

### What Needs to Be Built

| Component | Priority | Notes |
|-----------|----------|-------|
| Apify client service | 🔴 High | New service to call Apify API |
| TCGplayer URL mapping | 🔴 High | Map 18 boxes to TCGplayer product URLs |
| Scheduled job runner | 🟡 Medium | Daily automation (can use cron initially) |
| Data transformer | 🔴 High | Convert Apify response → our format |
| Error handling & retry | 🟡 Medium | Handle API failures gracefully |

---

## Step 2: Calculation Consistency

### Current Metrics We Track

| Metric | Current Source | Apify Source | Consistency Plan |
|--------|----------------|--------------|------------------|
| `floor_price_usd` | Screenshot | `lowSalePrice` | Use Apify `lowSalePrice` as floor |
| `boxes_sold_per_day` | Screenshot | `averageDailyQuantitySold` | Direct mapping ✅ |
| `daily_volume_usd` | Calculated | `marketPrice × quantitySold` | Calculate from Apify data |
| `active_listings_count` | Screenshot | ❌ Not available | **Manual screenshots still needed** |
| `boxes_added_today` | Calculated | ❌ Not available | Calculate from day-over-day listings |
| `unified_volume_usd` | 30d × daily | Sum buckets | Sum Apify bucket volumes |

### Calculation Formulas (Apify Data)

```python
# Daily volume from Apify bucket
daily_volume = bucket['marketPrice'] * bucket['quantitySold']

# 30-day volume (sum buckets)
volume_30d = sum(bucket['marketPrice'] * bucket['quantitySold'] for bucket in buckets[-30:])

# Average daily sales (direct from API)
boxes_sold_per_day = data['averageDailyQuantitySold']

# Floor price (from most recent bucket)
floor_price = buckets[-1]['lowSalePrice'] if buckets else data.get('marketPrice')
```

### Data Validation Rules

1. **Price sanity check:** $50 < floor_price < $10,000
2. **Volume sanity check:** daily_volume > 0 if boxes_sold > 0
3. **Sales correlation:** If sales reported, volume must exist
4. **Date continuity:** No gaps > 7 days without flagging

---

## Step 3: Integration Architecture

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Apify API      │────▶│  TCGplayer      │────▶│  Data           │
│  (Daily Cron)   │     │  Scraper        │     │  Transformer    │
└─────────────────┘     │  Service        │     └────────┬────────┘
                        └─────────────────┘              │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  historical_    │◀────│  JSON Storage   │◀────│  Merged Data    │
│  entries.json   │     │  Handler        │     │  (API + Manual) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         ▲
                                                         │
                        ┌─────────────────┐              │
                        │  Manual Entry   │──────────────┘
                        │  (Listings only)│
                        └─────────────────┘
```

### New Files to Create

```
app/
├── services/
│   └── tcgplayer_apify.py    # NEW: Apify client & data transformer
├── jobs/
│   └── daily_sync.py         # NEW: Scheduled job runner
└── config.py                 # UPDATE: Add APIFY_API_TOKEN
```

---

## Step 4: Questions for User

### Critical Questions

1. **TCGplayer URLs**
   - Do you have the exact TCGplayer product URLs for all 18 boxes?
   - Example: `https://www.tcgplayer.com/product/XXXXX/one-piece-...`
   - I can find them, but confirm you don't have a list already.

2. **Apify Account**
   - Have you created an Apify account yet?
   - Do you have an API token ready?

3. **Bucket Granularity**
   - The sample shows weekly buckets. Want me to test with a real OP box URL to confirm if recent data is daily?

4. **Listings Data**
   - Confirm: You'll continue manual screenshots for listings count only?
   - Frequency: Daily? Every few days?

5. **Historical Backfill**
   - Should we backfill historical data from Apify (if available)?
   - Or start fresh from today forward?

6. **Schedule Preference**
   - What time should daily sync run? (Recommend: 2 AM EST, after TCGplayer updates)
   - Want notification on failure?

### Nice-to-Have Questions

7. **Multiple Variants**
   - Some boxes have variants (OP-01 Blue/White). How does TCGplayer list these?
   - Separate product pages or one page with variants?

8. **Error Handling**
   - If Apify fails for a box, should we:
     - a) Use previous day's data
     - b) Skip that box entirely
     - c) Alert you immediately

9. **Data Merge Strategy**
   - If both Apify and manual entry exist for same date:
     - a) Prefer Apify (automated = consistent)
     - b) Prefer manual (human-verified)
     - c) Merge (Apify for sales, manual for listings)

---

## Implementation Phases

### Phase A: Setup (30 min)
- [ ] Add `apify-client` to requirements.txt
- [ ] Add `APIFY_API_TOKEN` to config
- [ ] Create TCGplayer URL mapping

### Phase B: Service Build (1-2 hours)
- [ ] Create `app/services/tcgplayer_apify.py`
- [ ] Implement data transformer
- [ ] Add error handling & validation

### Phase C: Integration (1 hour)
- [ ] Connect to existing historical_data.py
- [ ] Ensure calculations match existing methodology
- [ ] Test with one box (OP-13)

### Phase D: Automation (30 min)
- [ ] Create daily job script
- [ ] Setup cron or scheduler
- [ ] Add logging & monitoring

### Phase E: Validation (ongoing)
- [ ] Compare API data vs manual screenshots
- [ ] Verify calculations match
- [ ] Document any discrepancies

---

## TCGplayer Product URLs (To Fill)

| Set Code | Product Name | TCGplayer URL |
|----------|--------------|---------------|
| OP-01 Blue | Romance Dawn (Blue) | `TBD` |
| OP-01 White | Romance Dawn (White) | `TBD` |
| OP-02 | Paramount War | `TBD` |
| OP-03 | Pillars of Strength | `TBD` |
| OP-04 | Kingdoms of Intrigue | `TBD` |
| OP-05 | Awakening of the New Era | `TBD` |
| OP-06 | Wings of the Captain | `TBD` |
| OP-07 | 500 Years in the Future | `TBD` |
| OP-08 | Two Legends | `TBD` |
| OP-09 | Emperors in the New World | `TBD` |
| OP-10 | Royal Blood | `TBD` |
| OP-11 | A Fist of Divine Speed | `TBD` |
| OP-12 | Legacy of the Master | `TBD` |
| OP-13 | Carrying on His Will | `TBD` |
| EB-01 | Memorial Collection | `TBD` |
| EB-02 | Anime 25th Collection | `TBD` |
| PRB-01 | Premium Booster | `TBD` |
| PRB-02 | Premium Booster Vol. 2 | `TBD` |

---

## Cost Estimate

| Item | Monthly Cost |
|------|--------------|
| Apify Actor Rental | $10.00 |
| API Usage (18 boxes × 30 days) | ~$5-10 |
| **Total** | **~$15-20/month** |

**ROI:** Saves ~2-3 hours/day of manual screenshot work

---

## Next Steps

1. **Answer questions above** (especially #1-6)
2. **Create Apify account** if not done
3. **I'll build the integration** once questions are answered



## Overview

Integrating the Apify TCGplayer Sales History actor to automate sales data collection for all 18 One Piece booster boxes.

**Actor:** `scraped/tcgplayer-sales-history`  
**Cost:** $10/month + ~$5-10/month usage  
**Benefit:** Automates ~80% of daily data collection

---

## Step 1: Existing Infrastructure Audit ✅

### What Already Exists

| Component | Status | Location |
|-----------|--------|----------|
| Config placeholders for API keys | ✅ Ready | `app/config.py` (commented) |
| Historical data service | ✅ Ready | `app/services/historical_data.py` |
| Volume calculation service | ✅ Ready | `app/services/volume_calculation.py` |
| Daily snapshot function | ✅ Ready | `calculate_volume_from_daily_snapshots()` |
| UUID mapping (DB ↔ Leaderboard) | ✅ Ready | `DB_TO_LEADERBOARD_UUID_MAP` |
| Data storage (JSON) | ✅ Ready | `data/historical_entries.json` |

### What Needs to Be Built

| Component | Priority | Notes |
|-----------|----------|-------|
| Apify client service | 🔴 High | New service to call Apify API |
| TCGplayer URL mapping | 🔴 High | Map 18 boxes to TCGplayer product URLs |
| Scheduled job runner | 🟡 Medium | Daily automation (can use cron initially) |
| Data transformer | 🔴 High | Convert Apify response → our format |
| Error handling & retry | 🟡 Medium | Handle API failures gracefully |

---

## Step 2: Calculation Consistency

### Current Metrics We Track

| Metric | Current Source | Apify Source | Consistency Plan |
|--------|----------------|--------------|------------------|
| `floor_price_usd` | Screenshot | `lowSalePrice` | Use Apify `lowSalePrice` as floor |
| `boxes_sold_per_day` | Screenshot | `averageDailyQuantitySold` | Direct mapping ✅ |
| `daily_volume_usd` | Calculated | `marketPrice × quantitySold` | Calculate from Apify data |
| `active_listings_count` | Screenshot | ❌ Not available | **Manual screenshots still needed** |
| `boxes_added_today` | Calculated | ❌ Not available | Calculate from day-over-day listings |
| `unified_volume_usd` | 30d × daily | Sum buckets | Sum Apify bucket volumes |

### Calculation Formulas (Apify Data)

```python
# Daily volume from Apify bucket
daily_volume = bucket['marketPrice'] * bucket['quantitySold']

# 30-day volume (sum buckets)
volume_30d = sum(bucket['marketPrice'] * bucket['quantitySold'] for bucket in buckets[-30:])

# Average daily sales (direct from API)
boxes_sold_per_day = data['averageDailyQuantitySold']

# Floor price (from most recent bucket)
floor_price = buckets[-1]['lowSalePrice'] if buckets else data.get('marketPrice')
```

### Data Validation Rules

1. **Price sanity check:** $50 < floor_price < $10,000
2. **Volume sanity check:** daily_volume > 0 if boxes_sold > 0
3. **Sales correlation:** If sales reported, volume must exist
4. **Date continuity:** No gaps > 7 days without flagging

---

## Step 3: Integration Architecture

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Apify API      │────▶│  TCGplayer      │────▶│  Data           │
│  (Daily Cron)   │     │  Scraper        │     │  Transformer    │
└─────────────────┘     │  Service        │     └────────┬────────┘
                        └─────────────────┘              │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  historical_    │◀────│  JSON Storage   │◀────│  Merged Data    │
│  entries.json   │     │  Handler        │     │  (API + Manual) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         ▲
                                                         │
                        ┌─────────────────┐              │
                        │  Manual Entry   │──────────────┘
                        │  (Listings only)│
                        └─────────────────┘
```

### New Files to Create

```
app/
├── services/
│   └── tcgplayer_apify.py    # NEW: Apify client & data transformer
├── jobs/
│   └── daily_sync.py         # NEW: Scheduled job runner
└── config.py                 # UPDATE: Add APIFY_API_TOKEN
```

---

## Step 4: Questions for User

### Critical Questions

1. **TCGplayer URLs**
   - Do you have the exact TCGplayer product URLs for all 18 boxes?
   - Example: `https://www.tcgplayer.com/product/XXXXX/one-piece-...`
   - I can find them, but confirm you don't have a list already.

2. **Apify Account**
   - Have you created an Apify account yet?
   - Do you have an API token ready?

3. **Bucket Granularity**
   - The sample shows weekly buckets. Want me to test with a real OP box URL to confirm if recent data is daily?

4. **Listings Data**
   - Confirm: You'll continue manual screenshots for listings count only?
   - Frequency: Daily? Every few days?

5. **Historical Backfill**
   - Should we backfill historical data from Apify (if available)?
   - Or start fresh from today forward?

6. **Schedule Preference**
   - What time should daily sync run? (Recommend: 2 AM EST, after TCGplayer updates)
   - Want notification on failure?

### Nice-to-Have Questions

7. **Multiple Variants**
   - Some boxes have variants (OP-01 Blue/White). How does TCGplayer list these?
   - Separate product pages or one page with variants?

8. **Error Handling**
   - If Apify fails for a box, should we:
     - a) Use previous day's data
     - b) Skip that box entirely
     - c) Alert you immediately

9. **Data Merge Strategy**
   - If both Apify and manual entry exist for same date:
     - a) Prefer Apify (automated = consistent)
     - b) Prefer manual (human-verified)
     - c) Merge (Apify for sales, manual for listings)

---

## Implementation Phases

### Phase A: Setup (30 min)
- [ ] Add `apify-client` to requirements.txt
- [ ] Add `APIFY_API_TOKEN` to config
- [ ] Create TCGplayer URL mapping

### Phase B: Service Build (1-2 hours)
- [ ] Create `app/services/tcgplayer_apify.py`
- [ ] Implement data transformer
- [ ] Add error handling & validation

### Phase C: Integration (1 hour)
- [ ] Connect to existing historical_data.py
- [ ] Ensure calculations match existing methodology
- [ ] Test with one box (OP-13)

### Phase D: Automation (30 min)
- [ ] Create daily job script
- [ ] Setup cron or scheduler
- [ ] Add logging & monitoring

### Phase E: Validation (ongoing)
- [ ] Compare API data vs manual screenshots
- [ ] Verify calculations match
- [ ] Document any discrepancies

---

## TCGplayer Product URLs (To Fill)

| Set Code | Product Name | TCGplayer URL |
|----------|--------------|---------------|
| OP-01 Blue | Romance Dawn (Blue) | `TBD` |
| OP-01 White | Romance Dawn (White) | `TBD` |
| OP-02 | Paramount War | `TBD` |
| OP-03 | Pillars of Strength | `TBD` |
| OP-04 | Kingdoms of Intrigue | `TBD` |
| OP-05 | Awakening of the New Era | `TBD` |
| OP-06 | Wings of the Captain | `TBD` |
| OP-07 | 500 Years in the Future | `TBD` |
| OP-08 | Two Legends | `TBD` |
| OP-09 | Emperors in the New World | `TBD` |
| OP-10 | Royal Blood | `TBD` |
| OP-11 | A Fist of Divine Speed | `TBD` |
| OP-12 | Legacy of the Master | `TBD` |
| OP-13 | Carrying on His Will | `TBD` |
| EB-01 | Memorial Collection | `TBD` |
| EB-02 | Anime 25th Collection | `TBD` |
| PRB-01 | Premium Booster | `TBD` |
| PRB-02 | Premium Booster Vol. 2 | `TBD` |

---

## Cost Estimate

| Item | Monthly Cost |
|------|--------------|
| Apify Actor Rental | $10.00 |
| API Usage (18 boxes × 30 days) | ~$5-10 |
| **Total** | **~$15-20/month** |

**ROI:** Saves ~2-3 hours/day of manual screenshot work

---

## Next Steps

1. **Answer questions above** (especially #1-6)
2. **Create Apify account** if not done
3. **I'll build the integration** once questions are answered



