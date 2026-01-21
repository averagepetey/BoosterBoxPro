# 🚀 Launch Day Checklist

> **Purpose:** Everything you need to change/verify before going live with BoosterBoxPro.
> 
> **Estimated Time:** 30-60 minutes
> 
> **Last Updated:** January 21, 2026

---

## ⚠️ CRITICAL - Do These First

### 1. Update Environment to Production

**File:** `.env`

```bash
# Change this line:
ENVIRONMENT=production
```

**What this does:**
- Disables `/docs` and `/openapi.json` (hides API structure from attackers)
- Sanitizes error messages (no stack traces to users)
- Enforces JWT secret validation (fails if using default)
- Enables stricter security checks

---

### 2. Update CORS Origins

**File:** `.env`

```bash
# Replace with your actual domain(s):
CORS_ORIGINS=https://boosterboxpro.com,https://www.boosterboxpro.com
```

**What this does:**
- Only allows your frontend domain to call the API
- Blocks requests from other websites
- Prevents cross-site request attacks

**Note:** Include both `www` and non-`www` versions if you use both.

---

### 3. Verify JWT Secret is Set

**File:** `.env`

```bash
# Should be a long random string (64+ characters)
# NOT the default "change-me-in-production-use-strong-random-key"
JWT_SECRET_KEY=your-actual-secret-here
```

**To generate a new one:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

⚠️ **Warning:** Changing this will invalidate all existing user sessions.

---

### 4. Set Stripe Secrets (If Using Payments)

**File:** `.env`

```bash
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Where to find these:**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Make sure you're in **Live mode** (not Test mode)
3. Copy the keys

**Webhook Setup:**
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-api-domain.com/payment/webhook`
3. Select events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`
4. Copy the signing secret to `STRIPE_WEBHOOK_SECRET`

---

### 5. Set Admin IP Allowlist

**File:** `.env`

```bash
# Your IP addresses that can access /admin/* endpoints
# Get your IP: https://whatismyipaddress.com/
ADMIN_ALLOWED_IPS=YOUR_HOME_IP,YOUR_PHONE_IP

# Enable in production (auto-enabled when ENVIRONMENT=production)
ADMIN_IP_ALLOWLIST_ENABLED=true
```

**What this does:**
- Only allows specified IPs to access admin endpoints
- Even if someone steals admin credentials, they can't use them from other locations
- Blocks automated attacks on admin routes

**Examples:**
```bash
# Single IP
ADMIN_ALLOWED_IPS=203.0.113.50

# Multiple IPs
ADMIN_ALLOWED_IPS=203.0.113.50,198.51.100.25

# IP range (CIDR notation)
ADMIN_ALLOWED_IPS=203.0.113.0/24,198.51.100.25
```

**Note:** Localhost (127.0.0.1) is always allowed automatically.

---

## 🔐 Security Verification

### 5. Verify RLS is Enabled on Supabase

**Check in Supabase Dashboard:**
1. Go to SQL Editor
2. Run:
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```
3. All tables should show `rowsecurity = true`

**If not enabled, run the RLS script:**
- File: `Setup Guides/SUPABASE_RLS_SETUP.sql`

---

### 6. Verify Database Connection Uses SSL

**File:** `.env`

Your `DATABASE_URL` should include SSL parameters:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db?sslmode=require
```

---

### 7. Set Admin API Key (Optional but Recommended)

**File:** `.env`

```bash
# Generate a strong random key for admin endpoints
ADMIN_API_KEY=your-random-admin-key-here
```

**To generate:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🌐 Frontend Configuration

### 8. Update API Base URL

**File:** `frontend/.env.local` or `frontend/.env.production`

```bash
NEXT_PUBLIC_API_URL=https://api.boosterboxpro.com
```

**Or if API is on same domain:**
```bash
NEXT_PUBLIC_API_URL=https://boosterboxpro.com/api
```

---

### 9. Build Frontend for Production

```bash
cd frontend
npm run build
```

**Check for errors** - fix any build issues before deploying.

---

### 10. Verify CSP Headers

After deploying, check headers at [securityheaders.com](https://securityheaders.com)

**Expected headers:**
- ✅ Content-Security-Policy
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ Referrer-Policy
- ✅ Strict-Transport-Security (after HTTPS is set up)

---

## 🖥️ Deployment

### 11. Deploy Backend

**Options:**
- **Railway** - Easy Python hosting
- **Render** - Free tier available
- **AWS/GCP/Azure** - More control
- **VPS (DigitalOcean, Linode)** - Full control

**Environment variables to set on hosting platform:**
```
DATABASE_URL=...
ENVIRONMENT=production
JWT_SECRET_KEY=...
CORS_ORIGINS=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
ADMIN_API_KEY=...
```

---

### 12. Deploy Frontend

**Options:**
- **Vercel** - Best for Next.js (recommended)
- **Netlify** - Good alternative
- **Cloudflare Pages** - Fast CDN

**Environment variables:**
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

### 13. Set Up Custom Domain + HTTPS

1. Point your domain DNS to your hosting provider
2. Enable HTTPS/SSL (most hosts do this automatically)
3. Force HTTPS redirects

---

## ✅ Post-Launch Verification

### 14. Test Critical Flows

Run through these manually:

- [ ] **Homepage loads** - No console errors
- [ ] **Sign up** - New user can register
- [ ] **Login** - User can log in
- [ ] **Dashboard** - Loads with data (or paywall)
- [ ] **Admin access** - Your admin account works
- [ ] **Logout** - Clears session properly
- [ ] **API health** - `https://your-api.com/health` returns `{"status":"healthy"}`

---

### 15. Monitor for Errors

Set up error monitoring (optional but recommended):
- **Sentry** - Error tracking
- **LogRocket** - Session replay
- **Datadog** - Full observability

---

## 📋 Quick Reference: All Environment Variables

```bash
# === REQUIRED ===
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
ENVIRONMENT=production
JWT_SECRET_KEY=<64+ character random string>
CORS_ORIGINS=https://yourdomain.com

# === SECURITY (highly recommended) ===
ADMIN_ALLOWED_IPS=<your-ip>,<your-other-ip>
ADMIN_IP_ALLOWLIST_ENABLED=true

# === PAYMENTS (if using Stripe) ===
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# === OPTIONAL ===
ADMIN_API_KEY=<random string for admin endpoints>
REDIS_URL=<if using caching>
```

---

## 🚨 Emergency Rollback Plan

If something goes wrong:

1. **Revert to development mode:**
   ```bash
   ENVIRONMENT=development
   ```

2. **Check logs:**
   - Backend logs on your hosting platform
   - Browser console for frontend errors

3. **Database issues:**
   - Supabase has point-in-time recovery
   - Go to Supabase Dashboard → Settings → Database → Backups

4. **Invalidate all sessions (if compromised):**
   - Generate new JWT_SECRET_KEY
   - All users will need to log in again

---

## ✅ Final Checklist

Before announcing launch:

- [ ] `ENVIRONMENT=production` is set
- [ ] `CORS_ORIGINS` points to your domain
- [ ] `JWT_SECRET_KEY` is long and random
- [ ] RLS is enabled on Supabase
- [ ] HTTPS is working
- [ ] Stripe webhook is configured (if using payments)
- [ ] Tested signup/login flow
- [ ] Tested admin access
- [ ] No console errors on frontend
- [ ] API health check passes

---

**Good luck with your launch! 🎉**

