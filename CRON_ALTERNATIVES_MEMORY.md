# Run the daily refresh with more memory (free)

**Setup: cron runs only on GitHub.** See **`CRON_GITHUB_ONLY.md`** for the step-by-step (secrets, workflow, and turning off Render cron).

Render’s **free** cron jobs are limited to **512 MiB** RAM. The daily refresh (Apify + Playwright/Chromium scraper) exceeds that, so the job is run on **GitHub Actions** (~16 GB RAM, free) instead.

---

## Option A: GitHub Actions only (current setup – free, 16 GB RAM)

1. **Add secrets** (repo must have Actions enabled):
   - Repo → **Settings** → **Secrets and variables** → **Actions**
   - **New repository secret** for each:
     - **Name:** `DATABASE_URL`  
       **Value:** your Supabase/Postgres URL (same as Render `.env`).
     - **Name:** `APIFY_API_TOKEN`  
       **Value:** your Apify API token (same as Render `.env`).

2. **Workflow file** (already in the repo):
   - `.github/workflows/daily-refresh.yml`
   - Schedule: **1pm EST** (18:00 UTC) daily; also **Run workflow** manually from the Actions tab.

3. **Turn off Render cron** (required so the job runs only on GitHub):
   - Render → your cron job → **Settings** → disable or delete the cron job,  
   - or set **Schedule** to something that never runs (e.g. `0 0 31 2 *` = Feb 31).

**Notes:**
- Public repos: GitHub Actions minutes for scheduled workflows are free (within normal limits).
- Private repos: 2,000 free minutes/month; extra usage may incur cost.
- If the job fails with a missing library when running Playwright, add a step before “Run daily refresh”:  
  `run: playwright install-deps chromium`

---

## Option B: Keep Render cron with scraper skipped

If you prefer to keep everything on Render and only fix OOM:

1. In the **Cron Job** → **Environment**, add:
   - **SKIP_SCRAPER** = `1`
2. Redeploy/trigger a run.

Effect:
- **Phase 1 (Apify)** still runs → sales/volume data still updates.
- **Phase 2 (Listings scraper)** is skipped → listings-related metrics won’t refresh on cron; you can run the scraper locally when needed (e.g. `./scripts/run_daily_refresh_no_delay.sh`).

---

## Option C: Paid plan

Upgrade the Render cron job (or use a paid worker) to get more than 512 MiB so both Apify and the scraper can run on Render without `SKIP_SCRAPER`.

---

## Summary

| Where              | Memory   | Cost   | Both phases (Apify + Scraper) |
|--------------------|----------|--------|--------------------------------|
| Render free cron   | 512 MiB  | Free   | No (OOM)                      |
| Render + SKIP_SCRAPER | 512 MiB | Free   | No (scraper skipped)          |
| **GitHub Actions**  | **~16 GB** | **Free*** | **Yes**                   |
| Render paid        | 512 MiB+ | Paid   | Yes                           |

\* Free within GitHub’s Actions limits (public repos: generous; private: 2,000 min/month).
