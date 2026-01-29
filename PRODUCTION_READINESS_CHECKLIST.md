# Production Readiness Checklist

> **Goal:** Everything needed before going live with BoosterBoxPro  
> **Last Updated:** Jan 28, 2026  
> **Status:** ~75% Complete

---

## 🔴 CRITICAL (Must Do Before Launch)

### 1. Security & Configuration

**Location:** Render → API → Environment

- [ ] **ENVIRONMENT** = `production`
  - Disables `/docs` and `/openapi.json`
  - Sanitizes error messages
  - Enforces JWT secret validation

- [ ] **JWT_SECRET_KEY** = 64+ character random string
  - Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
  - Must NOT be `change-me-in-production-use-strong-random-key`
  - ⚠️ Changing this invalidates all existing sessions

- [ ] **CORS_ORIGINS** = your production frontend URL(s) only
  - Example: `https://boosterboxpro.vercel.app` or your custom domain
  - No wildcards (`*`) for strict security
  - Include both `www` and non-`www` if you use both

- [ ] **ADMIN_ALLOWED_IPS** = your IP(s), comma-separated
  - Get your IP: https://whatismyipaddress.com/
  - Example: `203.0.113.50` or `203.0.113.50,198.51.100.25`

- [ ] **ADMIN_IP_ALLOWLIST_ENABLED** = `true`
  - Restricts `/admin/*` endpoints to your IPs only

- [ ] **DATABASE_URL** includes `?sslmode=require` (or Supabase equivalent)
  - Supabase URLs usually already have SSL

- [ ] **Supabase RLS (Row Level Security)** enabled
  - Supabase → SQL Editor → run:
    ```sql
    SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
    ```
  - All tables should show `rowsecurity = true`
  - If not, run `Setup Guides/SUPABASE_RLS_SETUP.sql`

- [ ] **No secrets in git**
  - Run: `git grep -E 'sk_live_|sk_test_[a-zA-Z0-9]{24,}|whsec_[a-zA-Z0-9]{24,}|postgresql.*://[^@]+@' -- '*.py' '*.ts' '*.tsx' '*.env*' 2>/dev/null || true`
  - Review matches; remove or replace with placeholders
  - Ensure `.env` is in `.gitignore` (it is ✓)

**After setting these:** Redeploy the API so new env vars take effect.

---

### 2. Database Migrations

- [ ] **Run migrations in production**
  - Connect to production DB (via Render shell or Supabase SQL Editor)
  - Run: `alembic upgrade head`
  - Verify `users` table exists (migrations `004`, `007`)

---

### 3. Stripe (When Ready for Real Payments)

**If you're taking payments:**

- [ ] **Stripe Dashboard → Webhooks**
  - Add endpoint: `https://boosterboxpro.onrender.com/api/v1/payment/webhook`
  - Select events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`
  - Copy the signing secret

- [ ] **Render → API → Environment**
  - `STRIPE_WEBHOOK_SECRET` = webhook signing secret from Stripe

- [ ] **Switch to live keys** (when going live)
  - `STRIPE_SECRET_KEY` = `sk_live_...` (not `sk_test_...`)
  - `STRIPE_PUBLISHABLE_KEY` = `pk_live_...` (not `pk_test_...`)
  - Update in both Render (API) and Vercel (frontend: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`)

**Until then:** Test keys are fine for development.

---

## 🟡 IMPORTANT (Should Do Before Launch)

### 4. Data Quality & Validation

- [ ] **Run listings scraper for all boxes**
  - Verify floor prices are accurate
  - Check listings counts look reasonable
  - Ensure shipping costs are included in floor price

- [ ] **Validate Apify sales data**
  - Spot-check a few boxes on leaderboard
  - Ensure all boxes have recent data (last 7 days)
  - Backfill any missing historical data if needed

- [ ] **Verify all boxes have complete metrics**
  - Floor price
  - Active listings count
  - Volume (7d, 30d)
  - Sales data (from Apify)
  - All calculated metrics display correctly

**Estimated Time:** 1-2 hours

---

### 5. Frontend Cleanup

- [ ] **Releases page** (`frontend/app/(dashboard)/releases/page.tsx`)
  - Replace `// TODO: Replace with API call` with real API calls
  - Or hide/redirect if that page isn't used yet

- [ ] **ProtectedRoute** (`frontend/components/auth/ProtectedRoute.tsx`)
  - Re-enable auth check (currently disabled?)
  - Implement actual subscription status checking

- [ ] **Remove debug code**
  - Remove `console.log` statements from `SignupModal.tsx`
  - Remove debug comments from `dashboard/page.tsx`

- [ ] **Market Notes & Signals** (box detail page)
  - Implement or hide "No notes yet" section

**Estimated Time:** 1-2 hours

---

### 6. Monitoring & Alerts

- [ ] **Cron job failure alerts**
  - Set up notification when `boosterboxpro-daily-refresh` fails
  - Options: Render alerts, email, Slack webhook, or simple "last success" check in app

- [ ] **Uptime monitoring** (already have UptimeRobot ✓)
  - Verify it's still running and alerting correctly

**Estimated Time:** 30 minutes

---

## 🟢 NICE-TO-HAVE (Can Add Post-Launch)

### 7. Chrome Extension

- [ ] **Test on TCGplayer**
  - Load extension in Chrome
  - Visit a TCGplayer product page
  - Verify box metrics panel appears
  - Test popup auth/subscription

- [ ] **Polish & store submission**
  - Finalize popup UI
  - Write store description
  - Create screenshots
  - Submit to Chrome Web Store

**Estimated Time:** 2-3 days (can wait until post-launch)

---

### 8. Mobile Responsiveness

- [ ] **Mobile pass**
  - Test sign-in, dashboard, leaderboard, box detail on phone
  - Fix any layout/UX issues
  - Ensure touch targets are large enough

**Estimated Time:** 1-2 hours

---

### 9. Performance & Scaling

- [ ] **Render upgrade** (when traffic justifies)
  - Free tier has cold starts; upgrade to paid when you have users
  - Consider upgrading if cold starts hurt UX

- [ ] **CDN for images** (optional)
  - If box images are slow to load

---

## ✅ Already Done

- ✅ Backend on Render
- ✅ Frontend on Vercel
- ✅ All 12 Render env vars set
- ✅ CORS configured
- ✅ Auth & payments implemented in code
- ✅ Cron job running (daily refresh)
- ✅ DB-backed historical data
- ✅ Leaderboard speed optimizations
- ✅ Smoke-test passed (sign up, login, dashboard, leaderboard, box detail)
- ✅ Box detail auth token fix

---

## 📋 Quick Order (Recommended)

1. **Security pass** (30-60 min)
   - Set `ENVIRONMENT=production`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `ADMIN_ALLOWED_IPS`, `ADMIN_IP_ALLOWLIST_ENABLED=true`
   - Redeploy API
   - Verify RLS on Supabase
   - Check no secrets in git

2. **Run migrations** (5 min)
   - `alembic upgrade head` in production

3. **Data quality check** (1-2 hours)
   - Run listings scraper, spot-check Apify data

4. **Frontend cleanup** (1-2 hours)
   - Fix Releases page, ProtectedRoute, remove debug code

5. **Stripe webhook** (when ready for payments)
   - Add webhook in Stripe, set `STRIPE_WEBHOOK_SECRET` in Render

6. **Monitoring** (30 min)
   - Set up cron failure alerts

7. **Mobile pass** (1-2 hours)
   - Test on phone, fix issues

8. **Chrome extension** (post-launch)
   - Test, polish, submit to store

---

## 🚀 Launch Day

Once all **CRITICAL** items are done:

1. Final smoke-test on production
2. Announce/go live
3. Monitor logs for first 24 hours
4. Fix any issues that come up

---

**Ref:** `SECURITY_PASS_CHECKLIST.md`, `Setup Guides/LAUNCH_DAY_CHECKLIST.md`, `GRAND_TODO_LIST.md`
