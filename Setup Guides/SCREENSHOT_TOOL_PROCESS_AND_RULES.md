# Screenshot Tool Process and Rules

## Overview

Manual screenshot data entry process for extracting and recording booster box market data via chat with Claude.

---

## 📅 Date Rules

- Record entries for specific dates only (confirm dates before starting)
- Current session: **January 20, 2026** and **January 21, 2026**
- **Boxes Added Today**: Do NOT record - will be calculated by comparing consecutive days

---

## 📦 Inventory/Listings Rules

### What to Count
- ✅ Only count listings **up to +20% of floor price**
- ✅ English language listings only

### What to Exclude
- ❌ **Japanese listings** - Do NOT count
- ❌ Listings above +20% of floor price
- ❌ Non-English listings

### Example
If floor price is **$100**:
- Count listings from $100 to $120 (within +20%)
- Do NOT count listings at $121+

---

## 📊 Metrics to Extract

| Metric | Description | Notes |
|--------|-------------|-------|
| **Floor Price** | Lowest listing price (USD) | English only |
| **Active Listings** | Count within +20% of floor | English only, exclude Japanese |
| **Daily Volume** | Sales volume in USD | For the day |
| **Boxes Sold Today** | Number of units sold | For the day |
| **30d Volume** | 30-day volume | If visible |

### Metrics NOT to Record
- ❌ Boxes Added Today (calculated from day-over-day comparison)

---

## 🔄 Process Flow

1. **Send screenshot** of box data from TCGplayer/eBay
2. **Claude extracts** all visible metrics
3. **Claude formats** data for specified dates
4. **User confirms** accuracy
5. **Move to next box**
6. **After all boxes**: Data compiled into historical entries

---

## 🔁 Running Total Method (Duplicate Prevention)

**CRITICAL: Always use this method to prevent duplicate data**

### How It Works
1. User sends screenshot with sales data
2. Claude counts TOTAL sales shown in screenshot
3. Claude checks EXISTING data in system for that date
4. Claude calculates: `NEW = Screenshot Total - Existing Total`
5. Claude UPDATES the entry to the new total (not add on top)

### Example
```
Screenshot shows: 18 sales for Jan 21
Existing Jan 21: 12 sales
Difference: 6 NEW sales
Action: UPDATE Jan 21 to 18 sales (not 12+18=30)
```

### Rules
- ✅ Always compare screenshot totals vs existing data
- ✅ UPDATE existing entries, never create duplicates
- ✅ If screenshot total = existing total → No change needed
- ✅ If screenshot total > existing → Update to new total
- ❌ NEVER add screenshot total ON TOP of existing

---

## 📋 Box Checklist

| Set Code | Box Name | Jan 20 | Jan 21 |
|----------|----------|--------|--------|
| OP-01 Blue | Romance Dawn (Blue) | ✅ | ✅ |
| OP-01 White | Romance Dawn (White) | ✅ | ✅ |
| OP-02 | Paramount War | ✅ | ✅ |
| OP-03 | Pillars of Strength | ✅ | ✅ |
| OP-04 | Kingdoms of Intrigue | ✅ | ✅ |
| OP-05 | Awakening of the New Era | ✅ | ✅ |
| OP-06 | Wings of the Captain | ✅ | ✅ |
| OP-07 | 500 Years in the Future | ✅ | ✅ |
| OP-08 | Two Legends | ✅ | ✅ |
| OP-09 | Emperors in the New World | ✅ | ✅ |
| OP-10 | Royal Blood | ✅ | ✅ |
| OP-11 | A Fist of Divine Speed | ✅ | ✅ |
| OP-12 | Legacy of the Master | ✅ | ✅ |
| OP-13 | Carrying on His Will | ✅ | ✅ |
| EB-01 | Memorial Collection | ✅ | ✅ |
| EB-02 | Anime 25th Collection | ✅ | ✅ |
| PRB-01 | Premium Booster | ✅ | ✅ |
| PRB-02 | Premium Booster Vol. 2 | ✅ | ✅ |

---

## 📝 Data Entry Template

```json
{
  "date": "2026-01-21",
  "box_id": "uuid-here",
  "set_code": "OP-01",
  "floor_price_usd": 0.00,
  "active_listings_count": 0,
  "boxes_sold_today": 0,
  "daily_volume_usd": 0.00,
  "unified_volume_usd": 0.00
}
```

---

## ⚠️ Important Notes

1. **Consistency is key** - Use same methodology for all boxes
2. **Japanese exclusion** - Always filter out Japanese listings
3. **20% threshold** - Only count inventory within 20% of floor
4. **Boxes Added** - Never record directly; always calculate from comparison
5. **Double-check floor price** - This affects the 20% calculation

---

## 📊 Data Summary - January 20-21, 2026 Session

**Completed:** 2026-01-21

### Volume Summary

| Date | Total Boxes Sold | Total Volume |
|------|------------------|--------------|
| Jan 20, 2026 | 237 | $112,337.17 |
| Jan 21, 2026 | 66 | $53,321.58 |

### Per-Box Summary

| Box | Jan 20 Boxes | Jan 20 Volume | Jan 21 Boxes | Jan 21 Volume | Listings |
|-----|--------------|---------------|--------------|---------------|----------|
| OP-13 | 26 | $14,848.86 | 12 | $6,846.93 | 49 |
| OP-09 | 18 | $11,207.10 | 0 | $0 | 73 |
| EB-01 | 3 | $2,541.94 | 0 | $0 | 12 |
| OP-11 | 25 | $10,450.37 | 2 | $805.00 | 105 |
| OP-01 Blue | 0 | $0 | 0 | $0 | 11 |
| PRB-01 | 2 | $1,893.98 | 1 | $840.00 | 40 |
| OP-01 White | 2 | $4,083.85 | 1 | $2,113.38 | 11 |
| OP-05 | 4 | $4,150.00 | 11 | $12,071.91 | 18 |
| OP-10 | 13 | $2,989.52 | 4 | $928.73 | 520 |
| PRB-02 | 23 | $7,652.78 | 3 | $997.00 | 64 |
| OP-07 | 4 | $1,225.62 | 3 | $919.00 | 71 |
| OP-12 | 52 | $11,054.95 | 6 | $1,289.70 | 87 |
| OP-04 | 2 | $1,210.84 | 1 | $555.00 | 22 |
| OP-06 | 24 | $8,213.31 | 1 | $339.88 | 48 |
| EB-02 | 16 | $8,667.55 | 1 | $649.49 | 36 |
| OP-02 | 2 | $1,274.95 | 1 | $560.00 | 22 |
| OP-08 | 18 | $3,720.12 | 3 | $1,029.99 | 42 |
| OP-03 | 2 | $1,591.18 | 2 | $1,526.65 | 30 |

---

## 📜 Change Log

| Date | Change |
|------|--------|
| 2026-01-21 | Initial rules established |
| 2026-01-21 | Added: Only count listings within +20% of floor |
| 2026-01-21 | Added: Exclude Japanese listings |
| 2026-01-21 | Added: Do NOT record Boxes Added Today |
| 2026-01-21 | COMPLETED: All 18 boxes captured for Jan 20-21, 2026 |
| 2026-01-21 | Data imported to database and historical JSON |



## Overview

Manual screenshot data entry process for extracting and recording booster box market data via chat with Claude.

---

## 📅 Date Rules

- Record entries for specific dates only (confirm dates before starting)
- Current session: **January 20, 2026** and **January 21, 2026**
- **Boxes Added Today**: Do NOT record - will be calculated by comparing consecutive days

---

## 📦 Inventory/Listings Rules

### What to Count
- ✅ Only count listings **up to +20% of floor price**
- ✅ English language listings only

### What to Exclude
- ❌ **Japanese listings** - Do NOT count
- ❌ Listings above +20% of floor price
- ❌ Non-English listings

### Example
If floor price is **$100**:
- Count listings from $100 to $120 (within +20%)
- Do NOT count listings at $121+

---

## 📊 Metrics to Extract

| Metric | Description | Notes |
|--------|-------------|-------|
| **Floor Price** | Lowest listing price (USD) | English only |
| **Active Listings** | Count within +20% of floor | English only, exclude Japanese |
| **Daily Volume** | Sales volume in USD | For the day |
| **Boxes Sold Today** | Number of units sold | For the day |
| **30d Volume** | 30-day volume | If visible |

### Metrics NOT to Record
- ❌ Boxes Added Today (calculated from day-over-day comparison)

---

## 🔄 Process Flow

1. **Send screenshot** of box data from TCGplayer/eBay
2. **Claude extracts** all visible metrics
3. **Claude formats** data for specified dates
4. **User confirms** accuracy
5. **Move to next box**
6. **After all boxes**: Data compiled into historical entries

---

## 🔁 Running Total Method (Duplicate Prevention)

**CRITICAL: Always use this method to prevent duplicate data**

### How It Works
1. User sends screenshot with sales data
2. Claude counts TOTAL sales shown in screenshot
3. Claude checks EXISTING data in system for that date
4. Claude calculates: `NEW = Screenshot Total - Existing Total`
5. Claude UPDATES the entry to the new total (not add on top)

### Example
```
Screenshot shows: 18 sales for Jan 21
Existing Jan 21: 12 sales
Difference: 6 NEW sales
Action: UPDATE Jan 21 to 18 sales (not 12+18=30)
```

### Rules
- ✅ Always compare screenshot totals vs existing data
- ✅ UPDATE existing entries, never create duplicates
- ✅ If screenshot total = existing total → No change needed
- ✅ If screenshot total > existing → Update to new total
- ❌ NEVER add screenshot total ON TOP of existing

---

## 📋 Box Checklist

| Set Code | Box Name | Jan 20 | Jan 21 |
|----------|----------|--------|--------|
| OP-01 Blue | Romance Dawn (Blue) | ✅ | ✅ |
| OP-01 White | Romance Dawn (White) | ✅ | ✅ |
| OP-02 | Paramount War | ✅ | ✅ |
| OP-03 | Pillars of Strength | ✅ | ✅ |
| OP-04 | Kingdoms of Intrigue | ✅ | ✅ |
| OP-05 | Awakening of the New Era | ✅ | ✅ |
| OP-06 | Wings of the Captain | ✅ | ✅ |
| OP-07 | 500 Years in the Future | ✅ | ✅ |
| OP-08 | Two Legends | ✅ | ✅ |
| OP-09 | Emperors in the New World | ✅ | ✅ |
| OP-10 | Royal Blood | ✅ | ✅ |
| OP-11 | A Fist of Divine Speed | ✅ | ✅ |
| OP-12 | Legacy of the Master | ✅ | ✅ |
| OP-13 | Carrying on His Will | ✅ | ✅ |
| EB-01 | Memorial Collection | ✅ | ✅ |
| EB-02 | Anime 25th Collection | ✅ | ✅ |
| PRB-01 | Premium Booster | ✅ | ✅ |
| PRB-02 | Premium Booster Vol. 2 | ✅ | ✅ |

---

## 📝 Data Entry Template

```json
{
  "date": "2026-01-21",
  "box_id": "uuid-here",
  "set_code": "OP-01",
  "floor_price_usd": 0.00,
  "active_listings_count": 0,
  "boxes_sold_today": 0,
  "daily_volume_usd": 0.00,
  "unified_volume_usd": 0.00
}
```

---

## ⚠️ Important Notes

1. **Consistency is key** - Use same methodology for all boxes
2. **Japanese exclusion** - Always filter out Japanese listings
3. **20% threshold** - Only count inventory within 20% of floor
4. **Boxes Added** - Never record directly; always calculate from comparison
5. **Double-check floor price** - This affects the 20% calculation

---

## 📊 Data Summary - January 20-21, 2026 Session

**Completed:** 2026-01-21

### Volume Summary

| Date | Total Boxes Sold | Total Volume |
|------|------------------|--------------|
| Jan 20, 2026 | 237 | $112,337.17 |
| Jan 21, 2026 | 66 | $53,321.58 |

### Per-Box Summary

| Box | Jan 20 Boxes | Jan 20 Volume | Jan 21 Boxes | Jan 21 Volume | Listings |
|-----|--------------|---------------|--------------|---------------|----------|
| OP-13 | 26 | $14,848.86 | 12 | $6,846.93 | 49 |
| OP-09 | 18 | $11,207.10 | 0 | $0 | 73 |
| EB-01 | 3 | $2,541.94 | 0 | $0 | 12 |
| OP-11 | 25 | $10,450.37 | 2 | $805.00 | 105 |
| OP-01 Blue | 0 | $0 | 0 | $0 | 11 |
| PRB-01 | 2 | $1,893.98 | 1 | $840.00 | 40 |
| OP-01 White | 2 | $4,083.85 | 1 | $2,113.38 | 11 |
| OP-05 | 4 | $4,150.00 | 11 | $12,071.91 | 18 |
| OP-10 | 13 | $2,989.52 | 4 | $928.73 | 520 |
| PRB-02 | 23 | $7,652.78 | 3 | $997.00 | 64 |
| OP-07 | 4 | $1,225.62 | 3 | $919.00 | 71 |
| OP-12 | 52 | $11,054.95 | 6 | $1,289.70 | 87 |
| OP-04 | 2 | $1,210.84 | 1 | $555.00 | 22 |
| OP-06 | 24 | $8,213.31 | 1 | $339.88 | 48 |
| EB-02 | 16 | $8,667.55 | 1 | $649.49 | 36 |
| OP-02 | 2 | $1,274.95 | 1 | $560.00 | 22 |
| OP-08 | 18 | $3,720.12 | 3 | $1,029.99 | 42 |
| OP-03 | 2 | $1,591.18 | 2 | $1,526.65 | 30 |

---

## 📜 Change Log

| Date | Change |
|------|--------|
| 2026-01-21 | Initial rules established |
| 2026-01-21 | Added: Only count listings within +20% of floor |
| 2026-01-21 | Added: Exclude Japanese listings |
| 2026-01-21 | Added: Do NOT record Boxes Added Today |
| 2026-01-21 | COMPLETED: All 18 boxes captured for Jan 20-21, 2026 |
| 2026-01-21 | Data imported to database and historical JSON |



## Overview

Manual screenshot data entry process for extracting and recording booster box market data via chat with Claude.

---

## 📅 Date Rules

- Record entries for specific dates only (confirm dates before starting)
- Current session: **January 20, 2026** and **January 21, 2026**
- **Boxes Added Today**: Do NOT record - will be calculated by comparing consecutive days

---

## 📦 Inventory/Listings Rules

### What to Count
- ✅ Only count listings **up to +20% of floor price**
- ✅ English language listings only

### What to Exclude
- ❌ **Japanese listings** - Do NOT count
- ❌ Listings above +20% of floor price
- ❌ Non-English listings

### Example
If floor price is **$100**:
- Count listings from $100 to $120 (within +20%)
- Do NOT count listings at $121+

---

## 📊 Metrics to Extract

| Metric | Description | Notes |
|--------|-------------|-------|
| **Floor Price** | Lowest listing price (USD) | English only |
| **Active Listings** | Count within +20% of floor | English only, exclude Japanese |
| **Daily Volume** | Sales volume in USD | For the day |
| **Boxes Sold Today** | Number of units sold | For the day |
| **30d Volume** | 30-day volume | If visible |

### Metrics NOT to Record
- ❌ Boxes Added Today (calculated from day-over-day comparison)

---

## 🔄 Process Flow

1. **Send screenshot** of box data from TCGplayer/eBay
2. **Claude extracts** all visible metrics
3. **Claude formats** data for specified dates
4. **User confirms** accuracy
5. **Move to next box**
6. **After all boxes**: Data compiled into historical entries

---

## 🔁 Running Total Method (Duplicate Prevention)

**CRITICAL: Always use this method to prevent duplicate data**

### How It Works
1. User sends screenshot with sales data
2. Claude counts TOTAL sales shown in screenshot
3. Claude checks EXISTING data in system for that date
4. Claude calculates: `NEW = Screenshot Total - Existing Total`
5. Claude UPDATES the entry to the new total (not add on top)

### Example
```
Screenshot shows: 18 sales for Jan 21
Existing Jan 21: 12 sales
Difference: 6 NEW sales
Action: UPDATE Jan 21 to 18 sales (not 12+18=30)
```

### Rules
- ✅ Always compare screenshot totals vs existing data
- ✅ UPDATE existing entries, never create duplicates
- ✅ If screenshot total = existing total → No change needed
- ✅ If screenshot total > existing → Update to new total
- ❌ NEVER add screenshot total ON TOP of existing

---

## 📋 Box Checklist

| Set Code | Box Name | Jan 20 | Jan 21 |
|----------|----------|--------|--------|
| OP-01 Blue | Romance Dawn (Blue) | ✅ | ✅ |
| OP-01 White | Romance Dawn (White) | ✅ | ✅ |
| OP-02 | Paramount War | ✅ | ✅ |
| OP-03 | Pillars of Strength | ✅ | ✅ |
| OP-04 | Kingdoms of Intrigue | ✅ | ✅ |
| OP-05 | Awakening of the New Era | ✅ | ✅ |
| OP-06 | Wings of the Captain | ✅ | ✅ |
| OP-07 | 500 Years in the Future | ✅ | ✅ |
| OP-08 | Two Legends | ✅ | ✅ |
| OP-09 | Emperors in the New World | ✅ | ✅ |
| OP-10 | Royal Blood | ✅ | ✅ |
| OP-11 | A Fist of Divine Speed | ✅ | ✅ |
| OP-12 | Legacy of the Master | ✅ | ✅ |
| OP-13 | Carrying on His Will | ✅ | ✅ |
| EB-01 | Memorial Collection | ✅ | ✅ |
| EB-02 | Anime 25th Collection | ✅ | ✅ |
| PRB-01 | Premium Booster | ✅ | ✅ |
| PRB-02 | Premium Booster Vol. 2 | ✅ | ✅ |

---

## 📝 Data Entry Template

```json
{
  "date": "2026-01-21",
  "box_id": "uuid-here",
  "set_code": "OP-01",
  "floor_price_usd": 0.00,
  "active_listings_count": 0,
  "boxes_sold_today": 0,
  "daily_volume_usd": 0.00,
  "unified_volume_usd": 0.00
}
```

---

## ⚠️ Important Notes

1. **Consistency is key** - Use same methodology for all boxes
2. **Japanese exclusion** - Always filter out Japanese listings
3. **20% threshold** - Only count inventory within 20% of floor
4. **Boxes Added** - Never record directly; always calculate from comparison
5. **Double-check floor price** - This affects the 20% calculation

---

## 📊 Data Summary - January 20-21, 2026 Session

**Completed:** 2026-01-21

### Volume Summary

| Date | Total Boxes Sold | Total Volume |
|------|------------------|--------------|
| Jan 20, 2026 | 237 | $112,337.17 |
| Jan 21, 2026 | 66 | $53,321.58 |

### Per-Box Summary

| Box | Jan 20 Boxes | Jan 20 Volume | Jan 21 Boxes | Jan 21 Volume | Listings |
|-----|--------------|---------------|--------------|---------------|----------|
| OP-13 | 26 | $14,848.86 | 12 | $6,846.93 | 49 |
| OP-09 | 18 | $11,207.10 | 0 | $0 | 73 |
| EB-01 | 3 | $2,541.94 | 0 | $0 | 12 |
| OP-11 | 25 | $10,450.37 | 2 | $805.00 | 105 |
| OP-01 Blue | 0 | $0 | 0 | $0 | 11 |
| PRB-01 | 2 | $1,893.98 | 1 | $840.00 | 40 |
| OP-01 White | 2 | $4,083.85 | 1 | $2,113.38 | 11 |
| OP-05 | 4 | $4,150.00 | 11 | $12,071.91 | 18 |
| OP-10 | 13 | $2,989.52 | 4 | $928.73 | 520 |
| PRB-02 | 23 | $7,652.78 | 3 | $997.00 | 64 |
| OP-07 | 4 | $1,225.62 | 3 | $919.00 | 71 |
| OP-12 | 52 | $11,054.95 | 6 | $1,289.70 | 87 |
| OP-04 | 2 | $1,210.84 | 1 | $555.00 | 22 |
| OP-06 | 24 | $8,213.31 | 1 | $339.88 | 48 |
| EB-02 | 16 | $8,667.55 | 1 | $649.49 | 36 |
| OP-02 | 2 | $1,274.95 | 1 | $560.00 | 22 |
| OP-08 | 18 | $3,720.12 | 3 | $1,029.99 | 42 |
| OP-03 | 2 | $1,591.18 | 2 | $1,526.65 | 30 |

---

## 📜 Change Log

| Date | Change |
|------|--------|
| 2026-01-21 | Initial rules established |
| 2026-01-21 | Added: Only count listings within +20% of floor |
| 2026-01-21 | Added: Exclude Japanese listings |
| 2026-01-21 | Added: Do NOT record Boxes Added Today |
| 2026-01-21 | COMPLETED: All 18 boxes captured for Jan 20-21, 2026 |
| 2026-01-21 | Data imported to database and historical JSON |


