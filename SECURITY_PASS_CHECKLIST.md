# Security pass checklist

Use this on **Render → your API service → Environment**. Tick as you verify or set each item.

---

## 1. ENVIRONMENT=production

- [ ] **Render → API → Environment** → `ENVIRONMENT` = `production`
- **Why:** Turns off `/docs` and `/openapi.json`, sanitizes errors, enforces JWT secret check.

---

## 2. JWT_SECRET_KEY (64+ chars, not default)

- [ ] **Render → API → Environment** → `JWT_SECRET_KEY` is set
- [ ] Value is **64+ characters** and **not** `change-me-in-production-use-strong-random-key`
- **Generate:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Warning:** Changing it invalidates all existing sessions.

---

## 3. CORS_ORIGINS = only your frontend URL(s)

- [ ] **Render → API → Environment** → `CORS_ORIGINS` = your live frontend URL(s) only
- **Example:** `https://boosterboxpro.vercel.app` or `https://yourdomain.com,https://www.yourdomain.com`
- **No** `*` or `https://*.vercel.app` if you want strict lockdown (your app may use a regex for `*.vercel.app` — check `app/config.py` if unsure).
- **Why:** Only your frontend can call the API from the browser.

---

## 4. Admin IP allowlist

- [ ] **Render → API → Environment** → `ADMIN_ALLOWED_IPS` = your IP(s), comma-separated
  - Get your IP: https://whatismyipaddress.com/
  - Example: `203.0.113.50` or `203.0.113.50,198.51.100.25`
- [ ] **Render → API → Environment** → `ADMIN_IP_ALLOWLIST_ENABLED` = `true`
- **Why:** Only those IPs can hit `/admin/*`; reduces risk if admin credentials leak.

---

## 5. Database: SSL and RLS

- [ ] **DATABASE_URL** includes `?sslmode=require` (or Supabase’s equivalent). Supabase URLs often already use SSL.
- [ ] **Supabase → SQL Editor** run:
  ```sql
  SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
  ```
  All tables should show `rowsecurity = true`. If not, run `Setup Guides/SUPABASE_RLS_SETUP.sql`.

---

## 6. Stripe (when you go live for real payments)

- [ ] Use **live** keys: `STRIPE_SECRET_KEY=sk_live_...`, `STRIPE_PUBLISHABLE_KEY=pk_live_...`
- [ ] **Stripe Dashboard → Developers → Webhooks** → add `https://boosterboxpro.onrender.com/api/v1/payment/webhook` (or your real API URL)
- [ ] **Render** → `STRIPE_WEBHOOK_SECRET` = the webhook signing secret from Stripe.
- **Until then:** Test keys and test webhook are OK; switch to live when you enable payments.

---

## 7. No secrets in git

- [ ] No real `DATABASE_URL`, `JWT_SECRET_KEY`, Stripe keys, or API tokens in the repo.
- [ ] Docs use placeholders only. Run:
  ```bash
  git grep -E 'sk_live_|sk_test_[a-zA-Z0-9]{24,}|whsec_[a-zA-Z0-9]{24,}|postgresql.*://[^@]+@' -- '*.py' '*.ts' '*.tsx' '*.env*' 2>/dev/null || true
  ```
  (Review any matches; remove or replace with env/placeholder.)

---

## Quick order

1. **ENVIRONMENT=production** + **JWT_SECRET_KEY** + **CORS_ORIGINS** + **ADMIN_ALLOWED_IPS** + **ADMIN_IP_ALLOWLIST_ENABLED=true** in Render.  
2. **Redeploy** the API so new env vars are applied.  
3. **DATABASE_URL** + **RLS** and **no secrets in git** as above.  
4. **Stripe** when you’re ready for live payments.

---

**Ref:** `Setup Guides/LAUNCH_DAY_CHECKLIST.md`, `GRAND_TODO_LIST.md` → Security & config.
