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

## Writers: Use DB So the Site Updates Without Commits

For **new** scraped/imported data to show up on the deployed app without commits:

1. **Write to the database** (e.g. `box_metrics_unified`, `booster_boxes`) from:
   - Listings scraper
   - Daily refresh / Apify
   - Screenshot/chat/manual entry flows (e.g. `historical_data_manager` → also insert into `box_metrics_unified`)
   - Any script that currently appends to `historical_entries.json` or updates `leaderboard.json`

2. **Optional:** Keep writing JSON for local/backup, but treat DB as the source of truth for the live API.

3. **Deployed app:** Already reads from DB first. As long as writers update the DB (and you’ve run the backfill for existing history), the site reflects new data as soon as it’s in the DB—no deploy or commit of data files needed.

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
| `scripts/backfill_historical_json_to_db.py` | One-time backfill: `historical_entries.json` → `box_metrics_unified`. |
| `main.py` | No change; leaderboard already prefers DB and uses JSON as fallback. |

No changes to formulas, sort logic, or API response shape—only where historical rows are loaded from.
