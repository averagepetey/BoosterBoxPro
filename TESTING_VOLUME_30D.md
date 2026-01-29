# Testing 30d volume calculations manually

## 1. Run the verification script

Uses **OP-13** by default, or pass a box UUID:

```bash
python scripts/verify_30d_volume_calculations.py
python scripts/verify_30d_volume_calculations.py <box_id>
```

The script prints:

- **Entries in the last 30 days** and, for each, its contribution: `floor × boxes_sold_per_day × days_in_period`
- **Manual rolling total** (sum of those contributions)
- **Ramp formula** (when ≥2 entries): `30 × boxes_sold_30d_avg × (first_floor + current_floor) / 2`
- **Service results**: `get_box_30d_volume()`, `get_box_30d_volume_ramp_estimate()`, `get_box_30d_volume_or_ramp()`
- A **spot-check** that the manual rolling total matches `get_box_30d_volume()`

## 2. Check ramp vs rolling rule

- **Entries in last 30d < 7** → app uses **ramp** (first month).
- **Entries in last 30d ≥ 7** → app uses **rolling** total.

Compare script output to leaderboard or box-detail API for the same box.

## 3. Compare to API

- **Leaderboard**: `GET /booster-boxes` → check `metrics.volume_30d` for the box.
- **Box detail**: `GET /booster-boxes/{box_id}` → check `metrics.volume_30d` and `metrics.unified_volume_usd`.

## 4. Manual pencil check (rolling)

For one box, from `data/historical_entries.json`:

1. Find the box’s array of entries; filter to `date >= (today - 30 days)`.
2. Sort by date. For each entry, compute **days_in_period** (to next entry or to today, clamped to the 30d window).
3. For each: `contribution = floor_price_usd × boxes_sold_per_day × days_in_period`.
4. Sum contributions → that’s the rolling 30d volume. It should match `get_box_30d_volume()` and the script’s “Manual rolling total”.

## 5. Manual pencil check (ramp, first month)

When there are 2–6 entries in the last 30d:

1. **first_floor** = first entry’s `floor_price_usd`
2. **current_floor** = last entry’s `floor_price_usd`
3. **boxes_sold_30d_avg** = average of `boxes_sold_per_day` over those entries
4. **volume_30d** ≈ `30 × boxes_sold_30d_avg × (first_floor + current_floor) / 2`

That should match `get_box_30d_volume_ramp_estimate()` and the script’s “Manual ramp”.
