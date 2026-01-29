# How Volume Is Calculated

## Definitions

| Metric | Meaning | Where used |
|--------|--------|------------|
| **daily_volume_usd** | **Floor price × avg daily sold** for a single day | Box detail "Daily Volume", leaderboard when time range = 1d |
| **volume_7d** | **Running sum** of daily_volume_usd over the last 7 calendar days that have data | Leaderboard "Volume" when time range = 7d |
| **volume_30d** | **Running sum** of daily_volume_usd over the last 30 calendar days that have data | Leaderboard "Volume" when time range = 30d |
| **unified_volume_usd** | Usually = daily_volume_usd × 30 (extrapolated 30-day volume) | Fallback when volume_30d is missing |
| **unified_volume_7d_ema** | 7-day EMA of daily volume (alpha = 0.3); used for **sorting** leaderboard | Leaderboard sort, not displayed as a dollar sum |

---

## 1. Daily volume (`daily_volume_usd`)

**Formula:**
```text
daily_volume_usd = floor_price_usd × (boxes_sold_per_day or boxes_sold_30d_avg)
```
- No factor: we use **floor price × avg daily sold**.
- Example: floor $700, 18 boxes/day → **$12,600/day**.

**Sources (in order of use):**
- **Stored** `daily_volume_usd` (from screenshot/API) → use as-is.
- **Raw sales** for that day → sum of `(price + shipping) × quantity`.
- **Else** → `floor_price × sold` (no 92% or other adjustment).

**TCGplayer Apify:** `daily_volume_usd = floor × avg_daily` (floor used as price).
**historical_data:** Same formula when estimating; raw_sales sum when available.

---

## 2. 7d / 30d volume (`volume_7d`, `volume_30d`)

**Calculation (`get_rolling_volume_sum`, `get_all_boxes_latest_for_leaderboard`):**
```text
volume_7d  = sum(daily_volume_usd for each entry in last 7 calendar days)
volume_30d = sum(daily_volume_usd for each entry in last 30 calendar days)
```
- **Only days that have an entry** are summed.
- There is **no interpolation**: we do not fill missing days or multiply “one day” by 7/30.

**Example:**
- We have entries only on Jan 1, Jan 15, Jan 29 (3 days in 30).
- `volume_30d` = `daily_volume_usd(Jan 1) + daily_volume_usd(Jan 15) + daily_volume_usd(Jan 29)`.
- So it’s the **sum of 3 days of volume**, not “volume over 30 days.”

**Why it can look wrong:**  
If you expect “total volume over the last 30 days” but we only have a few snapshots, `volume_30d` will look **too low** because it’s the sum of a few daily values, not an extrapolated 30-day total.

**Fallback in the frontend:**  
If `volume_30d` is missing, the UI uses `unified_volume_usd` or `daily_volume_usd × 30`, which **are** 30-day extrapolations and will look **larger** than the strict `volume_30d` sum when data is sparse.

**December totals in historical data:**  
To improve accuracy of volume sums and 30d average sales, December 2025 is populated with multiple snapshot dates (Dec 4, 11, 18, 25, 30, 31) using the same December spreadsheet snapshot. That gives `volume_7d` / `volume_30d` and `get_box_30d_avg_sales` more data points in the 30-day window. Script: `scripts/add_december_totals_historical.py` (idempotent; run anytime to ensure December dates exist).

**Ramp-aware 30d volume guesstimate:**  
When price has moved a lot over the month (e.g. +300%), the strict sum of “each snapshot’s price × rate × days” understates volume because early days use the old price for long stretches. We therefore use a **guesstimate** that incorporates first-day and current price plus 30d average sales:

```text
volume_30d ≈ 30 × boxes_sold_30d_avg × (first_day_floor + current_floor) / 2
```

- **First-day floor:** floor price from the **oldest** entry in the last 30 days (start of period).
- **Current floor:** floor price from the **latest** entry (end of period).
- **boxes_sold_30d_avg:** average of `boxes_sold_per_day` over all entries in the 30-day window.

This assumes price moved **linearly** from first to current over 30 days (trapezoid rule). It is used when we have at least 2 entries in the 30-day window; otherwise we fall back to the strict sum or `daily × 30`. Implemented in `get_box_30d_volume_ramp_estimate()` and used for leaderboard and box-detail `volume_30d` / `unified_volume_usd`.

---

## 3. Unified 30-day volume (`unified_volume_usd`)

- **Stored** → use it.
- **Else** → `daily_volume_usd × 30` (extrapolated from one day’s floor × sold).
- Used as fallback when `volume_30d` (running sum) is missing.

---

## 4. 7-day EMA (`unified_volume_7d_ema`)

**Used for:** Leaderboard **sorting** (default sort by volume).

**Calculation in `get_box_price_history`:**
- EMA of **daily** volume with **alpha = 0.3** (per spec).
- First entry: `unified_volume_7d_ema = daily_volume_usd`.
- Next: `ema = (daily_volume_usd × 0.3) + (prev_ema × 0.7)`.
- Then we force: `unified_volume_7d_ema = max(calculated_ema, daily_volume_usd)`.

**Why it can look wrong:**  
The `max(..., daily_volume_usd)` means on a **spike day** the “7d EMA” can equal **today’s volume**, so it behaves more like “at least today” rather than a smooth 7-day average.

---

## Summary: Why Volume Doesn’t Look Correct

1. **Daily volume:** Apify uses 100% of price; other paths use ~92%. So the same box can show ~8% higher daily volume when sourced from Apify.
2. **volume_7d / volume_30d:** They are **sums of only the days we have data**. With sparse data (e.g. 3 days in 30), 30d volume looks **too low** compared to “daily × 30”.
3. **Fallback (daily × 30 or unified_volume_usd):** These are **extrapolated** and can be **much higher** than the strict `volume_30d` sum, so switching between “with fallback” and “without” can look inconsistent.
4. **unified_volume_7d_ema:** Capped below by today’s volume, so on spike days it doesn’t behave like a classic 7-day average.

---

## Possible Fixes (if you want to change behavior)

1. **Align daily volume with spec (92%):**  
   In Apify, set  
   `daily_vol = round(avg_daily * market_price * 0.92, 2)`  
   (and same for any other place that uses 100% of price for daily volume).

2. **Make 7d/30d “extrapolated” when data is sparse:**  
   e.g. If we have &lt; 7 entries in the last 7 days, set  
   `volume_7d = (sum of daily_volume_usd in window) / (number of days with data) * 7`  
   so the number represents “estimated 7-day volume” instead of “sum of 2–3 days.”

3. **Remove or relax the EMA cap:**  
   Use `unified_volume_7d_ema = calculated_ema` (or a gentler cap) so the 7d EMA is a true smoothed average and doesn’t jump to today’s volume on spikes.

If you tell me which of these you want (e.g. “use 92% everywhere” or “extrapolate 7d/30d when sparse”), I can point to the exact code and suggest a patch.
