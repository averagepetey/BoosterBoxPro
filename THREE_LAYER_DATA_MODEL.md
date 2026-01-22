# Three-Layer Data Model - Unified Timeline Architecture

## Core Principle

**"We maintain a single chronological observation stream per box. Historical inputs seed the early timeline. Daily screenshots are authoritative and override history on overlap. All derived metrics are recomputed from the unified timeline whenever new observations arrive."**

---

## The Three Layers

### Layer 1: Historical Baseline (Static Past)
**Purpose**: Establish baseline history for dates before daily tracking started

**Characteristics**:
- Entered once (or rarely corrected)
- May be less granular or precise
- Exists to avoid empty charts / broken averages
- **Should not change daily**

**Storage**: `data/historical_entries.json` (entries WITHOUT `source="screenshot"`)

**Example**:
```json
{
  "date": "2025-04-15",
  "floor_price_usd": 250.00,
  "boxes_sold_today": 5,
  "source": "historical"  // or no source field
}
```

---

### Layer 2: Daily Observations (Living Present)
**Purpose**: Authoritative record going forward from screenshot processing

**Characteristics**:
- Comes from screenshots (`enter_box_data.py` → `process_screenshot_data()`)
- Happens daily
- Higher confidence
- Used for all forward-looking signals
- **Overrides historical baseline for overlapping dates**

**Storage**: 
- `data/historical_entries.json` (entries WITH `source="screenshot"`)
- `box_metrics_unified` database table (derived metrics)

**Example**:
```json
{
  "date": "2026-01-04",
  "source": "screenshot",  // This marks it as authoritative
  "data_type": "combined",
  "floor_price_usd": 300.00,
  "boxes_sold_today": 12,
  "raw_listings": [...],
  "raw_sales": [...]
}
```

---

### Layer 3: Derived Metrics (Computed, Never Entered)
**Purpose**: What the app actually uses for display and calculations

**Characteristics**:
- Never stored independently
- Always computed from unified timeline
- Includes:
  - EMA (7-day exponential moving average)
  - 30-day averages
  - Liquidity score
  - Days-to-20% increase
  - Rankings

**Storage**: Calculated on-the-fly from unified timeline

**Key Rule**: **Derived metrics never care where data came from, only that inputs are ordered correctly**

---

## The Coexistence Rules

### Rule 1: Time-Based Ownership

For every box:
- **Historical baseline** owns dates ≤ cutoff date
- **Daily observations** own dates > cutoff date
- There should be a single cutoff date per box: "Daily tracking started on YYYY-MM-DD"

**Implementation**: Check `source="screenshot"` to identify daily observations

---

### Rule 2: Daily Data Always Wins on Overlap

**Scenario**:
- Historical input includes Jan 1
- Later add daily screenshot for Jan 1

**Result**:
- Historical record for Jan 1 is **ignored**
- Daily observation becomes **canonical**
- Historical data is **fallback, never authority**

**Implementation**: In `get_box_historical_data()`, daily observations (source="screenshot") completely replace historical baseline entries for the same date

---

### Rule 3: Both Feed the Same Derived Pipeline

**How it works**:
1. Derived metrics read historical inputs for early dates
2. Derived metrics read daily observations for later dates
3. Sort by date
4. Treat them as **one continuous time series**

**Implementation**: `get_box_historical_data()` returns unified chronological stream, `metrics_calculator` doesn't know/care which source provided the data

---

## How Unification Works

### Step 1: Load Both Sources
```python
# Load historical baseline from JSON
baseline_entries = load_from_json(box_id)

# Separate by source type
daily_observations = [e for e in baseline_entries if e.get("source") == "screenshot"]
historical_baseline = [e for e in baseline_entries if e.get("source") != "screenshot"]
```

### Step 2: Apply Override Logic
```python
# Daily observations override historical on same date
daily_by_date = {e.get("date"): e for e in daily_observations}

# Build unified timeline
unified = []
for historical_entry in historical_baseline:
    date = historical_entry.get("date")
    if date not in daily_by_date:
        # No daily observation for this date - use historical
        unified.append(historical_entry)

# Add all daily observations (they win on overlap)
unified.extend(daily_observations)
```

### Step 3: Sort Chronologically
```python
unified.sort(key=lambda x: x.get('date', ''))
```

### Step 4: Compute Derived Metrics
```python
# All derived metrics computed from unified timeline
metrics = calculate_metrics(unified_timeline)
# - EMA from last 7 entries
# - 30-day average from last 30 entries
# - etc.
```

---

## Data Flow Example

### Scenario: Processing screenshot for Jan 5, 2026

1. **Input**: Screenshot data for Jan 5
2. **Processing**:
   - Load unified timeline: historical baseline + existing daily observations
   - Add new daily observation for Jan 5 (source="screenshot")
   - If historical baseline has Jan 5 → it gets **replaced**
   - If daily observation already exists for Jan 5 → merge them
3. **Recalculation**:
   - Rebuild unified timeline
   - Recompute all derived metrics:
     - 7-day EMA (includes Jan 5)
     - 30-day average (includes Jan 5)
     - Volume → Liquidity → Days-to-20%
4. **Storage**:
   - Save to database (`box_metrics_unified`) with computed metrics
   - Save to JSON (`historical_entries.json`) with raw data + `source="screenshot"`

**Result**: All fields that depend on volume/metrics update together because they're all computed from the same unified timeline

---

## Key Implementation Points

### 1. Source Identification
- Daily observations: `source="screenshot"` in JSON entry
- Historical baseline: No source field OR `source="historical"`

### 2. Merging Logic
When same date has multiple entries:
- If any entry has `source="screenshot"` → use only those entries, ignore historical
- If multiple daily observations → merge them (sum sales, take best metrics)
- If only historical entries → merge them

### 3. Recalculation Trigger
Every time a daily screenshot is processed:
- Unified timeline is rebuilt
- All derived metrics are recomputed
- Database is updated with new metrics
- JSON is updated with new raw data

---

## Benefits of This Model

1. **Consistency**: One input → all metrics update together
2. **Authority**: Daily data always wins, no confusion
3. **Flexibility**: Historical baseline fills gaps without conflicts
4. **Accuracy**: Derived metrics always use most authoritative data
5. **Simplicity**: Single chronological stream = single source of truth for calculations

---

## File Locations

- **Unified Timeline Service**: `app/services/historical_data.py` → `get_box_historical_data()`
- **Merge Logic**: `app/services/historical_data.py` → `merge_same_date_entries()`
- **Processing Pipeline**: `scripts/automated_screenshot_processor.py` → `process_screenshot_data()`
- **Metrics Calculator**: `scripts/metrics_calculator.py` → `calculate_daily_metrics()`

---

## Mental Model Summary

**Think of it like a timeline with two types of entries**:

```
[Historical Baseline] ────────────────┐
                                       │
[Daily Observations]  ─────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │  Unified Timeline   │
                            │  (Single Stream)    │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │  Derived Metrics    │
                            │  (Computed)         │
                            └─────────────────────┘
```

**Daily observations overwrite historical baseline on overlap, but both contribute to the unified timeline used for all calculations.**




