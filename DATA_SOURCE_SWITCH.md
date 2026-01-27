# Data Source Switch: JSON → Database

Historical and leaderboard data now **prefer the database** so updates show on the live site **without commits**. JSON remains a fallback so nothing breaks.

---

## What Changed

### 1. Historical data (charts, 30d change, rolling volume, etc.)

- **Before:** Always read from `data/historical_entries.json`.
- **After:** Read from `box_metrics_unified` when the box has rows there; otherwise fall back to `historical_entries.json`.
- **Calculations:** Unchanged. Same formulas, same precedence, same entry shape. Only the **source** of the rows (DB vs file) changes.

### 2. Leaderboard “supplement” from `leaderboard.json`

- **Unchanged.** The API still loads `leaderboard.json` when present and uses it as fallback for `set_name`, `game_type`, `reprint_risk`, and metrics when the DB has no row. DB is already preferred when it has data.

---

## One-Time Backfill

To make the DB the source for historical data, backfill existing JSON into the DB:

```bash
# From repo root, with venv active and DATABASE_URL set
python scripts/backfill_historical_json_to_db.py
```

- Resolves leaderboard UUIDs to DB `booster_box_id` via `LEADERBOARD_TO_DB_UUID_MAP`.
- Upserts into `box_metrics_unified` on `(booster_box_id, metric_date)`.
- Skips entries whose `booster_box_id` doesn’t exist in `booster_boxes` (e.g. keys that were never migrated to DB).
- Safe to run multiple times.

After the backfill, leaderboard and box-detail “historical” logic will use DB for those boxes, and JSON only when the DB has no data.

---

## Writers: Wired to DB So the Site Updates Without Commits

Writers now call `app.services.box_metrics_writer.upsert_daily_metrics` so **new** scraped/imported data shows on the deployed app without commits:

| Writer | Where it’s wired | Fields written |
|--------|------------------|----------------|
| **Listings scraper** | `scripts/listings_scraper.save_results()` | `floor_price_usd`, `active_listings_count` |
| **Apify / daily refresh** | `app/services/tcgplayer_apify.refresh_all_boxes_sales_data()` | `floor_price_usd`, `boxes_sold_per_day`, `unified_volume_usd` |
| **Historical data manager** | `scripts/historical_data_manager.add_entry()` | `floor_price_usd`, `boxes_sold_per_day`, `active_listings_count`, `unified_volume_usd`, `boxes_added_today` (from `entry_data`) |

- JSON is still written for local/backup; DB is the source of truth for the live API.
- The deployed app reads from DB first. After backfill + writer wiring, the site reflects new data as soon as it’s in the DB—no deploy or commit of data files needed.

---

## Rollback

If you need to force JSON-only again:

- In `app/services/historical_data.py`, call `get_box_historical_data(box_id, prefer_db=False)` from the one place that passes the flag (or add a global/config switch and use it inside `get_box_historical_data`). Default remains `prefer_db=True`.

---

## Files Touched

| File | Role |
|------|------|
| `app/services/db_historical_reader.py` | Reads `box_metrics_unified` and returns the same entry shape as JSON. |
| `app/services/historical_data.py` | `get_box_historical_data(..., prefer_db=True)` tries DB first, then JSON. |
| `app/services/box_metrics_writer.py` | `upsert_daily_metrics(...)` writes one row into `box_metrics_unified`. |
| `scripts/backfill_historical_json_to_db.py` | One-time backfill: `historical_entries.json` → `box_metrics_unified`. |
| `scripts/listings_scraper.py` | `save_results()` calls `upsert_daily_metrics` per result. |
| `app/services/tcgplayer_apify.py` | `refresh_all_boxes_sales_data()` calls `upsert_daily_metrics` per box. |
| `scripts/historical_data_manager.py` | `add_entry()` calls `upsert_daily_metrics` after saving JSON (leaderboard→DB id mapping applied). |
| `main.py` | No change; leaderboard already prefers DB and uses JSON as fallback. |

No changes to formulas, sort logic, or API response shape—only where historical rows are loaded from.
