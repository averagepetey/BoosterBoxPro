# Daily refresh cron: GitHub only

The daily refresh (Apify + listings scraper) is set up to run **only on GitHub Actions**, not on Render. Follow these steps so the cron runs once per day on GitHub and not on Render.

---

## 1. Add GitHub secrets

- Repo → **Settings** → **Secrets and variables** → **Actions**
- **New repository secret** for each:

  | Name                      | Value                                                                 |
  |---------------------------|-----------------------------------------------------------------------|
  | `DATABASE_URL`            | Your Supabase/Postgres URL (same as Render)                           |
  | `APIFY_API_TOKEN`         | Your Apify API token (same as Render)                                 |
  | `BACKEND_URL`             | Your API base URL (e.g. `https://your-api.onrender.com`)              |
  | `INVALIDATE_CACHE_SECRET` | A secret string; set the same value as `INVALIDATE_CACHE_SECRET` on Render so the refresh can invalidate API caches and leaderboard/box detail update immediately after the run |

---

## 1b. Cache invalidation setup (step-by-step)

So leaderboard and box detail update right after the daily refresh, you need two places configured.

### Generate the secret (once)

In a terminal, run:

```bash
openssl rand -hex 32
```

Copy the output (e.g. `a1b2c3d4e5f6...`). You’ll use this **exact same value** in both GitHub and Render.

### GitHub Actions secrets

1. Open your repo on GitHub.
2. Click **Settings** (repo top bar).
3. In the left sidebar, under **Security**, click **Secrets and variables** → **Actions**.
4. Click **New repository secret**.
5. **Name:** `BACKEND_URL`  
   **Value:** Your API base URL, no trailing slash, e.g. `https://boosterboxpro-api.onrender.com`  
   Click **Add secret**.
6. Click **New repository secret** again.
7. **Name:** `INVALIDATE_CACHE_SECRET`  
   **Value:** paste the string you generated with `openssl rand -hex 32`  
   Click **Add secret**.

### Render (API service)

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Open the **service** that runs your API (the web service, not the cron job).
3. Go to **Environment** (left sidebar).
4. Click **Add Environment Variable**.
5. **Key:** `INVALIDATE_CACHE_SECRET`  
   **Value:** the **same** string you used for the GitHub secret `INVALIDATE_CACHE_SECRET`  
   Save.
6. If the service is already running, trigger a **Manual Deploy** (or push a commit) so the new env var is picked up.

After this, when the daily refresh finishes on GitHub, it will call your API’s `POST /admin/invalidate-cache` and caches will clear so the next request gets fresh data.

---

## 2. Push the workflow

The workflow is in `.github/workflows/daily-refresh.yml`. Push to `main` (or your default branch). After that, GitHub will run it on schedule and you can trigger it manually under **Actions** → **Daily Refresh (Apify + Scraper)** → **Run workflow**.

**Schedule:** 1pm EST (18:00 UTC) daily.

When the refresh completes, the script calls your API’s `POST /admin/invalidate-cache` (using `BACKEND_URL` and `INVALIDATE_CACHE_SECRET`) so leaderboard and box detail serve fresh data immediately.

---

## 3. Turn off the Render cron (required)

So the job runs **only** on GitHub:

- Open **Render** → your project → the **cron job** (e.g. `boosterboxpro-daily-refresh`).
- Either:
  - **Delete** the cron job, or
  - **Settings** → **Suspend** / disable it, or
  - Change **Schedule** to something that never runs (e.g. `0 0 31 2 *` = Feb 31).

After this, the daily refresh runs only on GitHub.

---

## Summary

| Step              | Action |
|-------------------|--------|
| 1. GitHub secrets | Add `DATABASE_URL`, `APIFY_API_TOKEN`, `BACKEND_URL`, and `INVALIDATE_CACHE_SECRET` in repo Actions secrets. |
| 2. Render env     | On your API service (Render), set `INVALIDATE_CACHE_SECRET` to the same value so the refresh can call `POST /admin/invalidate-cache` and clear caches. |
| 3. Workflow       | Already in repo; push to `main` if needed. |
| 4. Render         | Disable or delete the Render cron job. |

---

## How to test (manual run)

1. On GitHub: open your repo → **Actions**.
2. In the left sidebar, click **Daily Refresh (Apify + Scraper)**.
3. On the right, click **Run workflow** → choose branch (e.g. `main`) → **Run workflow**.
4. Click the new run to watch logs. It will install deps, Playwright Chromium, then run the script. A green check means it worked.

For more context (memory limits, alternatives), see `CRON_ALTERNATIVES_MEMORY.md`.

---

## Why didn’t the cron run today?

Common reasons the scheduled run doesn’t happen:

1. **Schedule time**  
   The job runs at **18:00 UTC** (1pm EST / 10am PST). If it’s still before that in your timezone, it hasn’t run yet. GitHub can also delay it by **15–30 minutes**.

2. **Workflow only on default branch**  
   Scheduled workflows run only from the **default branch** (usually `main`). If `daily-refresh.yml` exists only on another branch, the schedule will never run. Merge it into `main` and push.

3. **Repo treated as inactive**  
   If the repo has had **no pushes and no workflow runs for 60+ days**, GitHub may **stop running scheduled workflows**. Fix: run the workflow once manually (**Actions** → **Daily Refresh** → **Run workflow**), or push a commit. After that, the schedule usually starts again.

4. **Actions disabled**  
   In the repo **Settings** → **Actions** → **General**, ensure “Disable actions” is not selected.

5. **Fork**  
   In **forks**, scheduled workflows do not run by default. Use the upstream repo or run the workflow manually.

6. **Check run history**  
   In **Actions** → **Daily Refresh (Apify + Scraper)** → open the list of runs. If there’s no run for today at ~18:00 UTC, the schedule didn’t fire. Use **Run workflow** to run it now and confirm secrets/permissions are correct.
