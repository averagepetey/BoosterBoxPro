# Render cron – 5‑minute setup

Do this in the **Render dashboard** (same project as your API).

1. **New +** → **Cron Job**.
2. **Connect** the BoosterBoxPro repo, branch `main`.
3. **Settings**
   - **Name:** `boosterboxpro-daily-refresh`
   - **Schedule:** `0 18 * * *`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python scripts/daily_refresh.py`
4. **Environment** → Add (or use an env group):
   - `DATABASE_URL` = same as your API
   - `APIFY_API_TOKEN` = same as your API
5. **Create Cron Job** → then **Trigger Run** once to test.

Done. It runs daily at 1pm EST; the script adds a 0–30 min jitter. See `DAILY_REFRESH_CRON_SETUP.md` for details.
