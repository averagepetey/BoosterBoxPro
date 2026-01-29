# Import DATABASE_URL and APIFY_API_TOKEN into GitHub Actions

**Where your values are (copy from one of these):**

- **Local:** Open the file `.env` in the project root (BoosterBoxPro). The lines `DATABASE_URL=...` and `APIFY_API_TOKEN=...` contain the values. Copy only the part after the `=`.
- **Render:** Dashboard → your API service → **Environment** → copy the values for `DATABASE_URL` and `APIFY_API_TOKEN`.

**Do not paste these values anywhere except GitHub Secrets (and keep .env out of git).**

---

## Exact import steps (GitHub)

1. Open: **https://github.com/averagepetey/BoosterBoxPro**
2. Click **Settings** (repo top bar).
3. Left sidebar: **Secrets and variables** → **Actions**.
4. Click **"New repository secret"**.

---

### Secret 1: DATABASE_URL

- **Name (key):** type exactly: `DATABASE_URL`
- **Secret (value):** paste your full database URL (from `.env` or Render).  
  Example shape: `postgresql+asyncpg://...` or `postgresql://...` (your real value is long and has a password).
- Click **"Add secret"**.

---

### Secret 2: APIFY_API_TOKEN

- Click **"New repository secret"** again.
- **Name (key):** type exactly: `APIFY_API_TOKEN`
- **Secret (value):** paste your Apify API token (from `.env` or Render).  
  Example shape: `apify_api_...` (your real value is a long token).
- Click **"Add secret"**.

---

**Done.** You should see `DATABASE_URL` and `APIFY_API_TOKEN` in the list. The workflow uses these when you run "Daily Refresh (Apify + Scraper)".
