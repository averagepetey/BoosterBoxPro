# Testing the Daily Refresh

Ways to verify that the daily refresh updates all data and that leaderboard/box detail show it automatically.

---

## 1. Run the refresh manually

### Option A: Locally (full run)

```bash
# From project root; requires DATABASE_URL and APIFY_API_TOKEN in env
# Use python3 on macOS (python may not be installed)
python3 scripts/daily_refresh.py --no-delay
```

- **Phase 1 (Apify)** should log `✅ Apify Success: N boxes` and write sales/volume to DB.
- **Phase 2 (Scraper)** should log `Saved {box_id}: listings=... | added=X, removed=Y (vs yesterday)` and write floor, listings, `boxes_added_today` to DB.
- If `BACKEND_URL` and `INVALIDATE_CACHE_SECRET` are set, you should see: `✅ API caches invalidated – leaderboard and box detail will serve fresh data`.
- If either is missing, you’ll see a **warning** that leaderboard/box detail won’t auto-update until cache TTL expires.

### Option B: GitHub Actions (workflow_dispatch)

1. Repo → **Actions** → **Daily Refresh (Apify + Scraper)**.
2. **Run workflow** → **Run workflow**.
3. Open the run and check the **Run daily refresh** step logs for the same messages as above.

---

## 2. Check status and logs

After a run (local or Actions):

```bash
# Status summary (local runs only – writes to logs/daily_refresh_status.json)
python3 scripts/check_daily_refresh_status.py
```

- Expect **Phase 1: Apify** and **Phase 2: Scraper** both completed with success counts.
- Local log file: `logs/daily_refresh.log`.

---

## 3. Verify data in the API

Use the verification script (see below) or call the API yourself.

**Leaderboard** (should reflect today’s metrics after cache invalidation):

```bash
# Replace with your API base URL and auth if required
curl -s "https://YOUR-API-URL/booster-boxes?limit=3" | python -m json.tool
```

Check a few boxes for:

- `floor_price_usd`, `active_listings_count`, `boxes_sold_30d_avg`, `unified_volume_usd`, `boxes_added_today` (when available).

**Box detail** (single box):

```bash
# Replace BOX_ID with a real UUID from leaderboard response
curl -s "https://YOUR-API-URL/booster-boxes/BOX_ID" | python -m json.tool
```

Check `data.metrics` for:

- `floor_price_usd`, `active_listings_count`, `boxes_sold_per_day`, `boxes_sold_30d_avg`, `boxes_added_today`, `daily_volume_usd`, `unified_volume_usd`.

---

## 4. Verify cache invalidation (auto-update)

1. **Before refresh**: Open dashboard leaderboard and one box detail; note current values (e.g. floor price, “Added Today”, Sold/Day).
2. **Run refresh** (local `python scripts/daily_refresh.py --no-delay` or Actions workflow_dispatch).
3. **After refresh**: Reload leaderboard and box detail (no hard refresh needed if you’re not caching in the browser).
4. **Expect**: Values update to the latest from the run (and “Added Today” shows a number when yesterday’s data existed).

If you did **not** set `BACKEND_URL` and `INVALIDATE_CACHE_SECRET` in the environment used by the refresh, the UI may show old data until the cache TTL (e.g. 30 min) expires. In that case you should see the warning in the refresh logs.

---

## 5. Verification script (optional)

From project root, with backend running and env set:

```bash
# Set your API base URL (no trailing slash)
export BACKEND_URL="https://your-api.run.app"   # or http://localhost:8000

# Run the script (uses unauthenticated GET; if your API requires auth, add a token to the script or use curl with -H "Authorization: Bearer ...")
python3 scripts/verify_daily_refresh_api.py
```

The script fetches the leaderboard and one box detail and prints key metrics so you can confirm they look correct after a refresh.

---

## Quick checklist

| Step | What to check |
|------|----------------|
| 1 | Run `python3 scripts/daily_refresh.py --no-delay` (local or via Actions). |
| 2 | Logs show Apify success + Scraper “Saved … added=X, removed=Y” for boxes. |
| 3 | Logs show “API caches invalidated” (or warning if BACKEND_URL/INVALIDATE_CACHE_SECRET missing). |
| 4 | `python3 scripts/check_daily_refresh_status.py` shows both phases completed. |
| 5 | Leaderboard API returns recent `floor_price_usd`, `unified_volume_usd`, etc. |
| 6 | Box detail API returns `boxes_added_today`, `boxes_sold_per_day`, `daily_volume_usd`. |
| 7 | After a refresh, reload dashboard/box detail and see updated numbers. |

---

## Workflow ran but box detail / leaderboard not updating

If the GitHub Actions workflow runs but the box detail page (or leaderboard) still shows old data or "—":

1. **Check workflow logs** (Actions → latest run → "Run daily refresh"):
   - Do you see **"✅ API caches invalidated"**? If yes, the backend was told to clear caches; if the page still doesn't update, the backend may be reading from a different DB or the frontend may be caching.
   - Do you see **"BACKEND_URL not set"** or **"INVALIDATE_CACHE_SECRET not set"**? Then the workflow never called your backend, so caches were not cleared. Add both secrets in the repo (Settings → Secrets and variables → Actions).
   - Do you see **"Invalidate cache failed: HTTP 401"**? Then the secret doesn't match: `INVALIDATE_CACHE_SECRET` in GitHub must equal the same env var on your **deployed** backend.
   - Do you see **"Could not invalidate API cache: …"** (e.g. timeout)? Then the workflow can't reach `BACKEND_URL` – use your **public** API URL (e.g. `https://your-app.run.app`), not localhost.

2. **Same DB**: The workflow writes to the DB using `DATABASE_URL` in GitHub secrets. Your **deployed backend** must use the **same** `DATABASE_URL`. If the backend uses a different DB, it will never see the new rows.

3. **Backend env**: On the host where your API runs (Cloud Run, Render, etc.), set `INVALIDATE_CACHE_SECRET` to the same value you put in GitHub secrets so the backend accepts the invalidation request.
