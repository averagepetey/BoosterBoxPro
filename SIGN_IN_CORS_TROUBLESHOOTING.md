# Sign-in / CORS troubleshooting (Vercel → Render)

If sign-in on Vercel shows **“Cannot connect to backend”**, **“Failed to fetch”**, or **“Database connection error. Please try again.”**:

**“Not Found” (404)**  
Usually means the login request is hitting the wrong host (e.g. your Vercel URL instead of your backend). Set **NEXT_PUBLIC_API_URL** on Vercel to your **Render backend** URL (e.g. `https://boosterboxpro.onrender.com`), then redeploy.

**“Cannot connect” / “Failed to fetch”**  
Often CORS or backend unreachable; see below.

**“Database connection error. Please try again.”**  
The request reached the backend but the DB failed during login. On Render, check **DATABASE_URL** in the API’s **Environment** tab: it must be your Supabase connection string with `?sslmode=require` (e.g. `postgresql+asyncpg://...@db.xxxxx.supabase.co:5432/postgres?sslmode=require`). The backend uses `ssl.create_default_context()` when `sslmode=require` is present. If it still fails, confirm Supabase allows connections from Render and that the URL has no typos.

**Note:** The backend allows **all `https://*.vercel.app`** origins by default. If you’re signing in from a Vercel deployment, CORS should work. If you use a custom domain or still see errors, use the steps below.

---

## 1. Use the exact origin in CORS_ORIGINS

- **Render** → your Web Service → **Environment** → **CORS_ORIGINS**.
- Value must be the **exact** URL you see in the browser when signing in, with **no trailing slash**.
  - OK: `https://your-app.vercel.app`
  - Bad: `https://your-app.vercel.app/`
  - Bad: `https://www.your-app.vercel.app` if you actually use `https://your-app.vercel.app`

Multiple origins: comma-separated, no spaces inside URLs:
```
https://your-app.vercel.app,https://your-app-git-main-you.vercel.app
```

The backend now strips trailing slashes from each origin, but the rest must match exactly.

---

## 2. Save and wait for Render to redeploy

After changing **CORS_ORIGINS**, save. Render will redeploy. Wait until the service is “Live” again (often 1–2 minutes), then try sign-in again.

---

## 3. Confirm Vercel’s API URL (fixes “Not Found” 404)

- **Vercel** → Project → **Settings** → **Environment Variables**.
- **NEXT_PUBLIC_API_URL** must be your **Render backend** URL, e.g. `https://boosterboxpro.onrender.com` (no trailing slash).
- **Wrong:** your Vercel frontend URL (e.g. `https://your-app.vercel.app`) → that causes 404 because there is no `/api/v1/auth/login` on Vercel.
- If you change it, **redeploy** the frontend (Deployments → … → Redeploy) so the new value is used; `NEXT_PUBLIC_*` is baked in at build time.

---

## 4. Backend may be sleeping (Render free tier)

If the backend was idle for a while, the first request can take 30–60 seconds or fail.

- Open `https://your-render-url.onrender.com/health` in a new tab and wait for `{"status":"healthy"}`.
- Then try sign-in again.

---

## 5. Check what origin the frontend is using

The sign-in error message now includes the **exact origin** the browser is sending (e.g. `https://your-app.vercel.app`). Copy that into **CORS_ORIGINS** on Render.

---

## 6. Multiple Vercel URLs (production vs preview)

- **Production:** `https://your-project.vercel.app`
- **Preview:** `https://your-project-git-branch-username.vercel.app`

If you sign in from a preview deployment, that preview URL must be in **CORS_ORIGINS** as well (comma-separated).

---

## Backend changes in this repo

- **CORS_ORIGINS** parsing strips trailing slashes so `https://app.vercel.app/` still matches `https://app.vercel.app`.
- If **CORS_ORIGINS** is empty or invalid in production, the backend logs a warning at startup.
- The sign-in error message includes the current origin so you can paste it into Render.
