# Render cron – 5‑minute setup

Do this in the **Render dashboard** (same project as your API).

---

## 1. Create the Cron Job

- **New +** → **Cron Job**.
- **Connect** the BoosterBoxPro repo, branch `main`.
- **Name:** `boosterboxpro-daily-refresh`

---

## 2. Where Build and Command are

Render’s cron form is like a Web Service: scroll the page. You’ll see:

- **Build** (or **Build & Deploy**)  
  - **Build Command:** `PIP_ROOT_USER_ACTION=ignore pip install -r requirements.txt`  
  - *(The `PIP_ROOT_USER_ACTION=ignore` part silences the “Running pip as the 'root' user” warning; you can omit it if you don’t care about that.)*  
  - Sometimes this is under a “Build” or “Build settings” / “Build & Deploy” section.

- **Schedule** and **Command** (cron-specific, often lower on the page or in a “Cron” / “Schedule” section)  
  - **Schedule:** `0 18 * * *`  
  - **Command:** `python scripts/daily_refresh.py`  
  - This “Command” is what runs every run. Render may label it “Command” or “Start command.”

If you only see one **Command** field in the cron area, that’s the one that runs on schedule — use `python scripts/daily_refresh.py` there, and put `PIP_ROOT_USER_ACTION=ignore pip install -r requirements.txt` in the **Build Command** field in the Build section above.

---

## 3. Environment: DATABASE_URL and APIFY_API_TOKEN

Add these two variables in the Cron Job’s **Environment** → **Add Environment Variable**. Use these values (same as in `RENDER_ENV_VARS_QUICK_COPY.md` / your API):

**DATABASE_URL**  
*(Copy from your Render API’s Environment tab, or from your .env. Use the same Supabase/Postgres URL you use for the API.)*

**APIFY_API_TOKEN**  
*(Same value as in your Render API’s Environment. Copy from there or from your .env; it’s not stored in the repo for security.)*

In the Cron Job form: **Environment** → **Add Environment Variable** → create `DATABASE_URL` and `APIFY_API_TOKEN` and paste the same values you use in your API (from its Environment tab or your .env).

If you use an **Environment Group** that already has these, you can attach that group to the Cron Job instead.

---

## 4. Finish and test

- **Create Cron Job** (or **Save**).
- On the cron job’s page, click **Trigger Run** once to test.

Done. It runs daily at 1pm EST; the script adds a 0–30 min jitter. See `DAILY_REFRESH_CRON_SETUP.md` for details.

---

## 5. If cron fails: "Out of memory (used over 512Mi)"

Render’s **free** cron jobs have a **512 MiB** memory limit. The daily refresh runs **Apify** (Phase 1) and a **Playwright/Chromium** listings scraper (Phase 2). Chromium can exceed 512 MiB.

**Try in this order:**

1. **Reduce Chromium memory**  
   In the Cron Job’s **Environment**, add:
   - **CRON_LOW_MEMORY** = `1`  
   This uses a smaller viewport and extra Chromium flags to lower memory. Redeploy and trigger a run.

2. **Skip the scraper (Phase 2) on cron**  
   If it still OOMs, you can run only Apify on Render and run the scraper elsewhere (e.g. locally):
   - **SKIP_SCRAPER** = `1`  
   Phase 1 (Apify sales data) still runs; Phase 2 (listings scraper) is skipped. Leaderboard sales/volume data will still update; only listings-related metrics won’t refresh on cron.

3. **Upgrade plan**  
   Paid Render plans give more RAM (e.g. 512 MiB+). Upgrading the cron job’s instance allows both phases to run without SKIP_SCRAPER.
