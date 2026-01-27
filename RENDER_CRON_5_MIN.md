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
```
postgresql+asyncpg://postgres.umjtdtksqxtyqeqddwkv:Chessmoves4321!@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```

**APIFY_API_TOKEN**  
*(Same value as in your Render API’s Environment. Copy from there or from your .env; it’s not stored in the repo for security.)*

In the Cron Job form: **Environment** → **Add Environment Variable** → create `DATABASE_URL` and `APIFY_API_TOKEN` and paste the values above.

If you use an **Environment Group** that already has these, you can attach that group to the Cron Job instead.

---

## 4. Finish and test

- **Create Cron Job** (or **Save**).
- On the cron job’s page, click **Trigger Run** once to test.

Done. It runs daily at 1pm EST; the script adds a 0–30 min jitter. See `DAILY_REFRESH_CRON_SETUP.md` for details.
