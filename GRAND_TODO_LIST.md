# Grand List – BoosterBoxPro

> One master checklist. **Last updated:** Jan 28, 2026 (audited against codebase)

---

## Done

- [x] Backend on Render (`https://boosterboxpro.onrender.com`)
- [x] All 12 Render env vars set (incl. `CORS_ORIGINS`, `ADMIN_API_KEY`, `ADMIN_ALLOWED_IPS`)
- [x] `python-multipart` added (fixes form-data / login)
- [x] HEAD supported on `/` and `/health` (UptimeRobot no longer gets 405)
- [x] UptimeRobot monitor on `https://boosterboxpro.onrender.com/` or `/health` (every 5 min)
- [x] Health check returns `{"status":"healthy"}` (or root `{"message":"BoosterBoxPro API","status":"running"}`)
- [x] DB-backed historical: reader + `prefer_db=True`; backfill run; writers wired to `box_metrics_unified` (listings scraper, Apify, historical_data_manager) so new scraped/imported data appears without commits — see `DATA_SOURCE_SWITCH.md`
- [x] Push latest commits — Render deploys DB-backed historical + leaderboard batch/skeleton (confirmed pushed)
- [x] Cron: daily refresh (Apify + listings scraper) running in production — `boosterboxpro-daily-refresh` cron job, user confirmed it runs
- [x] Auth & payments **implemented in code**: users table migrations (`004`, `007`), `app/models/user.py`, `app/utils/password.py`, `app/utils/jwt.py`, `app/repositories/user_repository.py`, `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `get_current_user`, `require_active_subscription` (paywall), `app/services/stripe_service.py`, `app/services/subscription_service.py`, `app/routers/payment.py` (incl. `POST /api/v1/payment/webhook`), `GET /api/v1/users/me`, subscription endpoints; leaderboard/box/time-series use paywall when auth is loaded
- [x] Chrome extension **structure in repo**: Manifest V3, `background.js`, `content/tcgplayer.js`, `content/panel.css`, popup (html/js/css), icons 16/48/128 — not yet in store
- [x] Leaderboard speed: batch DB queries, skeleton, two-phase load (fast 25 → full 100)
- [x] Frontend deployed to Vercel (user confirmed)

---

## Backend & deploy (next)

- [ ] (Optional) Stripe webhook **configuration**: In Stripe Dashboard add `https://boosterboxpro.onrender.com/api/v1/payment/webhook`; in Render set `STRIPE_WEBHOOK_SECRET`. Code already has the route.

---

## Frontend & launch

- [x] Deploy frontend to Vercel — use **Root Directory: `frontend`**; see `VERCEL_DEPLOYMENT.md` — **done**
- [x] Set `NEXT_PUBLIC_API_URL=https://boosterboxpro.onrender.com` in Vercel env — **done**
- [x] Set `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` in Vercel (if using Stripe) — **done**
- [x] In Render env, set `CORS_ORIGINS` to your Vercel URL — **done**
- [x] Redeploy backend after changing CORS — **done**
- [ ] Smoke-test: sign up, login, dashboard, leaderboard, box detail

---

## Auth & payments (pre-monetization)

**Implemented in code** (see Done above). Remaining is production config: run migrations in prod, set Stripe keys/webhook secret, optional lock-down of leaderboard/box/time-series to require auth.

- [x] Users table + migration (Alembic) — `004_add_users_table.py`, `007_add_user_subscription_fields.py`
- [x] User model, password util, JWT util, user repo — `app/models/user.py`, `app/utils/password.py`, `app/utils/jwt.py`, `app/repositories/user_repository.py`
- [x] `POST /api/v1/auth/register` and `POST /api/v1/auth/login` — `app/routers/auth.py`
- [x] `get_current_user` dependency; leaderboard/box/time-series use `require_active_subscription` when auth loaded — `main.py`, `app/dependencies/paywall.py`
- [x] Stripe: create-checkout / subscription flow + webhook handler — `app/routers/payment.py`, `app/services/stripe_service.py`
- [x] Paywall: `require_active_subscription` and trial logic — `app/dependencies/paywall.py`, `app/services/subscription_service.py`
- [x] Endpoints: `GET /api/v1/users/me`, `GET /api/v1/users/me/subscription`, `POST .../subscription/cancel` — `app/routers/user.py`, payment router

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

- [x] Cron/scripts: daily refresh (Apify), listings scraper; run in production — **done** (user confirmed cron runs)
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

---

## Lists audit (Jan 28, 2026)

**COMPLETE_REMAINING_TASKS_CHECKLIST.md** and **PRE_LAUNCH_CHECKLIST.md** say "Auth 0%", "Stripe 0%", "Production 0%", "Chrome extension 0%". **Reality vs codebase:**

- **Auth:** Implemented — `app/routers/auth.py` (register, login), `app/models/user.py`, `app/utils/password.py`, `app/utils/jwt.py`, `app/repositories/user_repository.py`, migrations `004_add_users_table.py`, `007_add_user_subscription_fields.py`, `get_current_user` in auth.
- **Stripe:** Implemented — `app/services/stripe_service.py`, `app/services/subscription_service.py`, `app/routers/payment.py` (webhook at `POST /api/v1/payment/webhook`), `app/dependencies/paywall.py` (`require_active_subscription`).
- **Production:** Backend is on Render; frontend deploy (Vercel) and env (CORS, NEXT_PUBLIC_API_URL) are config steps, not "0%".
- **Chrome extension:** Repo has Manifest V3, background, content script, popup, icons — structure exists; "0%" referred to store submission / full polish.
- **Cron:** Daily refresh cron is running (user confirmed).

Use **GRAND_TODO_LIST** above for accurate done/next; treat COMPLETE_REMAINING / PRE_LAUNCH as detailed task breakdowns, not source-of-truth for "what’s implemented."
