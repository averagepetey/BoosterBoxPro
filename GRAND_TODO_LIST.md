# Grand List – BoosterBoxPro

> One master checklist. **Last updated:** Jan 25, 2026

---

## Done

- [x] Backend on Render (`https://boosterboxpro.onrender.com`)
- [x] All 12 Render env vars set (incl. `CORS_ORIGINS`, `ADMIN_API_KEY`, `ADMIN_ALLOWED_IPS`)
- [x] `python-multipart` added (fixes form-data / login)
- [x] HEAD supported on `/` and `/health` (UptimeRobot no longer gets 405)
- [x] UptimeRobot monitor on `https://boosterboxpro.onrender.com/` or `/health` (every 5 min)
- [x] Health check returns `{"status":"healthy"}` (or root `{"message":"BoosterBoxPro API","status":"running"}`)
- [x] DB-backed historical: reader + `prefer_db=True`; backfill run; writers wired to `box_metrics_unified` (listings scraper, Apify, historical_data_manager) so new scraped/imported data appears without commits — see `DATA_SOURCE_SWITCH.md`

---

## Backend & deploy (next)

- [ ] Push latest commits so Render deploys DB-backed historical + writer wiring (then confirm deploy)
- [ ] (Optional) Stripe webhook in Render: add endpoint  
  `https://boosterboxpro.onrender.com/api/v1/payment/webhook` in Stripe Dashboard and set `STRIPE_WEBHOOK_SECRET` in Render
- [ ] **Then:** Frontend deploy (see **Frontend & launch** below).

---

## Frontend & launch

- [ ] Deploy frontend to Vercel (or other host)
- [ ] Set `NEXT_PUBLIC_API_URL=https://boosterboxpro.onrender.com`
- [ ] Set `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` (if using Stripe)
- [ ] In Render env, set `CORS_ORIGINS` to your real frontend URL (e.g. `https://yourapp.vercel.app`)
- [ ] Redeploy backend after changing CORS
- [ ] Smoke-test: sign up, login, dashboard, leaderboard, box detail

---

## Auth & payments (pre-monetization)

- [ ] Users table + migration (Alembic)
- [ ] User model, password util, JWT util, user repo
- [ ] `POST /api/v1/auth/register` and `POST /api/v1/auth/login`
- [ ] `get_current_user` dependency; protect leaderboard, box detail, time-series
- [ ] Stripe: create-checkout / subscription flow + webhook handler
- [ ] Paywall: `require_active_subscription` and trial logic
- [ ] Endpoints: `GET /api/v1/users/me`, `GET /api/v1/users/me/subscription`, `POST .../subscription/cancel`

---

## Data & quality

- [ ] Run listings scraper for all boxes; verify floor prices and listings counts
- [ ] Validate Apify sales data and backfill missing history
- [ ] Ensure all boxes have floor price, listings, volume, 7d/30d metrics where applicable
- [ ] (Optional) Admin workflow to set “reprint risk” and show it in the UI

---

## Chrome extension (TCGplayer)

- [ ] Manifest V3, background service worker, content script for TCGplayer pages
- [ ] Popup: auth, subscription status, preferences
- [ ] Panel/overlay: box metrics on product pages; product↔box matching + cache
- [ ] Icons, store listing, privacy policy; submit to Chrome Web Store

---

## Security & config (launch day)

- [ ] `ENVIRONMENT=production` in production
- [ ] `JWT_SECRET_KEY` long and random (64+ chars)
- [ ] `CORS_ORIGINS` = only production frontend URL(s)
- [ ] `ADMIN_ALLOWED_IPS` set; `ADMIN_IP_ALLOWLIST_ENABLED=true`
- [ ] Stripe: live keys and live webhook secret when going live
- [ ] DB URL with `?sslmode=require`; RLS enabled (Supabase)
- [ ] Confirm no `.env` or secrets in git

---

## Later / ongoing

- [ ] Cron/scripts: daily refresh (Apify), listings scraper; run in production
- [ ] Alerts if Apify/scraper fail
- [ ] Mobile responsiveness pass
- [ ] Upgrade Render when traffic justifies (e.g. avoid cold starts)

---

## Quick reference

| What | Where |
|------|--------|
| Backend URL | `https://boosterboxpro.onrender.com` |
| Health | `https://boosterboxpro.onrender.com/health` |
| Env vars | `RENDER_ENV_VARS_QUICK_COPY.md` |
| Deploy steps | `RENDER_DEPLOYMENT_GUIDE.md` |
| Full task detail | `COMPLETE_REMAINING_TASKS_CHECKLIST.md`, `PRE_LAUNCH_CHECKLIST.md` |
