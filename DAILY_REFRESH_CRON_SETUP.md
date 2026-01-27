# Daily Refresh Cron Job – 1pm EST

Runs **Apify** (sales data) then **listings scraper** every day at **1pm EST**.

---

## Schedule and Randomness

- **Cron** runs at **1pm EST** (18:00 UTC): `0 18 * * *`
- The script **sleeps a random 0–30 minutes** before doing any work.
- So the actual Apify + scraper run happens at a **random time between 1:00 and 1:30 PM EST**—same 1pm window, variable exact minute. This avoids a fixed hit time every day.
- During daylight saving (EDT), 1pm local = 17:00 UTC → use `0 17 * * *` for 1pm in summer.

---

## Option A: Add via Render Dashboard (recommended)

Use this if your API is already a **Web Service** created by hand.

1. **Render Dashboard** → same project as your API → **New +** → **Cron Job**.

2. **Connect repo**: same GitHub repo as your API (e.g. `BoosterBoxPro`). Same branch (e.g. `main`).

3. **Settings**
   - **Name**: `boosterboxpro-daily-refresh` (or any name)
   - **Schedule**: `0 18 * * *` (1pm EST; script adds 0–30 min jitter so work runs randomly within 1–1:30 PM)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scripts/daily_refresh.py`

4. **Environment variables** (required; use same values as your API):
   - `DATABASE_URL` – Postgres connection string
   - `APIFY_API_TOKEN` – Apify API token

   Optionally use an **Environment Group** that already has these, and attach that group to this Cron Job.

5. **Create Cron Job**. Render will build and then run the start command on the schedule.

6. **Trigger Run** (optional): Cron Job detail page → **Trigger Run** to run once immediately and check logs.

---

## Option B: Add via Blueprint (`render.yaml`)

This repo’s `render.yaml` defines a cron job. To create **only** the cron (and not touch an existing Web Service):

1. **Dashboard** → **Blueprints** → **New Blueprint Instance**.
2. Connect the **BoosterBoxPro** repo.
3. Render will show the cron job from `render.yaml`. When prompted, set:
   - `DATABASE_URL`
   - `APIFY_API_TOKEN`
4. Complete creation. The cron runs at 1pm EST (18:00 UTC); the script adds a random 0–30 min delay so the real run is somewhere between 1:00 and 1:30 PM EST.

If you prefer not to use the blueprint, ignore `render.yaml` and use **Option A** only.

---

## What it runs

- **Random delay**: 0–30 minutes after cron fires at 1pm EST (so the run is randomly between 1:00 and 1:30 PM, not the same second every day).
- **Phase 1**: Apify – fetches TCGplayer sales data for all boxes.
- **Phase 2**: Listings scraper – after Apify finishes, scrapes active listings and writes to the same DB.

Order is fixed: delay → Apify → listings scraper (see `scripts/daily_refresh.py`).

**Manual run (no delay)**: `python scripts/daily_refresh.py --no-delay`

---

## Logs and status

- **Render**: Cron Job → **Logs** for each run.
- **In repo** (when run locally): `logs/daily_refresh.log`, `logs/daily_refresh_status.json`.

---

## Cost

Render Cron Jobs are billed per run time; there is a **minimum of $1/month** per cron service. See [Render Cron Jobs](https://render.com/docs/cronjobs).
