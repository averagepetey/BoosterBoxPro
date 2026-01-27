# Vercel Deployment – BoosterBoxPro Frontend

Deploy the Next.js frontend to Vercel and connect it to the Render backend.

---

## Prerequisites

- GitHub repo connected (e.g. `averagepetey/BoosterBoxPro`)
- Backend live on Render: `https://boosterboxpro.onrender.com`

---

## 1. Create project on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in (GitHub).
2. **Add New** → **Project**.
3. **Import** your `BoosterBoxPro` repo.
4. **Root Directory:** set to `frontend` (click **Edit** next to the repo name and set **Root Directory** to `frontend`).
5. **Framework Preset:** Next.js (auto-detected).
6. **Build Command:** `npm run build` (default).
7. **Output Directory:** leave default (Next.js handles it).

---

## 2. Environment variables (Vercel)

In **Settings → Environment Variables**, add:

| Name | Value | Notes |
|------|--------|--------|
| `NEXT_PUBLIC_API_URL` | `https://boosterboxpro.onrender.com` | No trailing slash. Used by API routes and CSP. |

Optional (Stripe, etc.):

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Your Stripe publishable key (if you use Stripe on the client) |

Save and trigger a new deployment if the project already exists.

---

## 3. Deploy

Click **Deploy**. After the first deploy you’ll get a URL like:

`https://boosterboxpropro-xxx.vercel.app`  
or a custom domain if you add one.

---

## 4. Backend CORS (Render)

So the browser can call the Render API from your Vercel URL:

1. Open [Render Dashboard](https://dashboard.render.com) → your **Web Service** → **Environment**.
2. Set **CORS_ORIGINS** to your Vercel URL, e.g.:
   ```text
   https://boosterboxpropro-xxx.vercel.app
   ```
   Or, if you use a custom domain:
   ```text
   https://yourdomain.com
   ```
   For multiple origins (preview + prod), comma-separate:
   ```text
   https://boosterboxpropro-xxx.vercel.app,https://yourdomain.com
   ```
3. **Save Changes**. Render will redeploy.

---

## 5. Smoke test

1. Open your Vercel URL.
2. Check: landing, login/signup (if enabled), dashboard, leaderboard, box detail.
3. Open DevTools → Network and confirm requests to `https://boosterboxpro.onrender.com` return 200 (not CORS errors).

---

## Quick reference

| Item | Value |
|------|--------|
| Frontend root | `frontend` |
| Required env (Vercel) | `NEXT_PUBLIC_API_URL=https://boosterboxpro.onrender.com` |
| Backend | `https://boosterboxpro.onrender.com` |
| CORS | Set `CORS_ORIGINS` in Render to your Vercel (and custom) URLs |

---

## Troubleshooting

- **CORS errors:** Update `CORS_ORIGINS` in Render to include the exact Vercel URL (scheme + host, no path). Redeploy the Render service after changing env.
- **404 on API:** Ensure `NEXT_PUBLIC_API_URL` has no trailing slash and is the Render root (e.g. `https://boosterboxpro.onrender.com`).
- **Build fails:** Run `cd frontend && npm ci && npm run build` locally and fix any TypeScript or build errors.

### "Serverless Function has exceeded the unzipped maximum size of 250 MB"

1. **Root Directory must be `frontend`**  
   In Vercel → Project → Settings → General, set **Root Directory** to `frontend`. If it’s blank or `.`, the whole repo is used and the function can blow past 250 MB.

2. **Turn off “Include source files outside of the Root Directory”**  
   In Project → Settings → Git, disable **Include source files outside of the Root Directory** if it’s on. You want only the `frontend` folder in the build.

3. **See what’s large**  
   Add env var `NEXT_DEBUG_FUNCTION_SIZE=1` (or `VERCEL_BUILDER_DEBUG=1`) in Vercel, redeploy, and check the build logs for function size breakdown.

4. **Exclusions are in `frontend/next.config.ts`**  
   `outputFileTracingExcludes` already skips dev deps (TypeScript, ESLint, etc.), non-Linux native binaries (`@next/swc-darwin*`, `lightningcss-darwin*`), and `.next/cache` / `public`. If you’re still over after (1) and (2), use the debug env var to find the heaviest paths and add more exclusions.
