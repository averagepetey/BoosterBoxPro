# Daily refresh cron: GitHub only

The daily refresh (Apify + listings scraper) is set up to run **only on GitHub Actions**, not on Render. Follow these steps so the cron runs once per day on GitHub and not on Render.

---

## 1. Add GitHub secrets

- Repo → **Settings** → **Secrets and variables** → **Actions**
- **New repository secret** for each:

  | Name             | Value                                      |
  |------------------|--------------------------------------------|
  | `DATABASE_URL`   | Your Supabase/Postgres URL (same as Render) |
  | `APIFY_API_TOKEN`| Your Apify API token (same as Render)      |

---

## 2. Push the workflow

The workflow is in `.github/workflows/daily-refresh.yml`. Push to `main` (or your default branch). After that, GitHub will run it on schedule and you can trigger it manually under **Actions** → **Daily Refresh (Apify + Scraper)** → **Run workflow**.

**Schedule:** 1pm EST (18:00 UTC) daily.

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
| 1. GitHub secrets | Add `DATABASE_URL` and `APIFY_API_TOKEN` in repo Actions secrets. |
| 2. Workflow       | Already in repo; push to `main` if needed. |
| 3. Render         | Disable or delete the Render cron job. |

---

## How to test (manual run)

1. On GitHub: open your repo → **Actions**.
2. In the left sidebar, click **Daily Refresh (Apify + Scraper)**.
3. On the right, click **Run workflow** → choose branch (e.g. `main`) → **Run workflow**.
4. Click the new run to watch logs. It will install deps, Playwright Chromium, then run the script. A green check means it worked.

For more context (memory limits, alternatives), see `CRON_ALTERNATIVES_MEMORY.md`.
