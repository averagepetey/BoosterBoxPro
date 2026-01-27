# 🚀 Production Deployment Guide

> **Complete step-by-step guide to deploy BoosterBoxPro to production**  
> **Estimated Time:** 2-4 hours  
> **Last Updated:** January 26, 2026

---

## 📋 Pre-Deployment Checklist

Before starting, ensure you have:
- [ ] GitHub repository is up to date
- [ ] All environment variables documented
- [ ] Domain name ready (optional, can use provider subdomain initially)
- [ ] Stripe account with live keys (if using payments)
- [ ] Supabase database set up and accessible

---

## 🎯 Step 1: Choose Hosting Providers

### Backend (FastAPI)
**Recommended for Free:** Render (best free tier)
- **Render**: ✅ **FREE tier available** - Best option for $0/month
  - 750 hours/month (enough for 24/7)
  - Services sleep after 15 min inactivity (wakes on request)
  - Perfect for development and low-traffic production
  - Upgrade to $7/month "Starter" for always-on when needed
- **Railway**: $5/month minimum (after $5 free credit)
  - Better performance, always-on
  - Good if you have small budget
- **Alternative**: AWS/GCP/Azure (more complex but more control)

**💡 Recommendation:** Start with **Render Free Tier** (completely free), upgrade later if needed.

### Frontend (Next.js)
**Recommended:** Vercel
- **Vercel**: Built by Next.js creators, best integration
- **Alternative**: Netlify or Cloudflare Pages

### Database
**Already using:** Supabase PostgreSQL
- No changes needed, just ensure production database is accessible

---

## 🔧 Step 2: Prepare Deployment Files

### 2.1 Create Procfile for Backend (Railway/Render)

Create `Procfile` in root directory:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 2.2 Create runtime.txt (Python version)

Create `runtime.txt`:
```
python-3.11.0
```

### 2.3 Verify requirements.txt exists
✅ Already exists at root level

---

## 🌐 Step 3: Deploy Backend API

### Option A: Railway (Recommended for Simplicity)

1. **Sign up at [railway.app](https://railway.app)**
   - Connect your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `BoosterBoxPro` repository

3. **Configure Service**
   - Railway will auto-detect Python
   - Set root directory to `/` (root of repo)
   - Build command: (auto-detected, or `pip install -r requirements.txt`)
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   Go to Variables tab and add:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres.umjtdtksqxtyqeqddwkv:Chessmoves4321!@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
   ENVIRONMENT=production
   JWT_SECRET_KEY=tXbFlD96NTtBs52ZaIataOYNODXuUPJKksSeerKkDiEm4G0QKF1DkTE3NaxfIHO05ZFRFkroNd7NqNiatygSCQ
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://yourdomain.com
   STRIPE_SECRET_KEY=sk_live_xxx (or sk_test_xxx for testing)
   STRIPE_PUBLISHABLE_KEY=pk_live_xxx (or pk_test_xxx for testing)
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   STRIPE_PRICE_ID_PRO_PLUS=price_1StEqdKDTumXT1F1ft6PlwAP
   APIFY_API_TOKEN=your_apify_api_token_here
   ADMIN_API_KEY=your-secret-api-key-here
   ADMIN_ALLOWED_IPS=YOUR_IP_ADDRESS
   ADMIN_IP_ALLOWLIST_ENABLED=true
   ```

5. **Deploy**
   - Railway will automatically deploy on push to main branch
   - Wait for deployment to complete
   - Copy the generated URL (e.g., `https://boosterboxpro-production.up.railway.app`)

6. **Set Custom Domain (Optional)**
   - Go to Settings → Domains
   - Add your custom domain (e.g., `api.boosterboxpro.com`)
   - Update DNS records as instructed

### Option B: Render

1. **Sign up at [render.com](https://render.com)**
   - Connect your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `BoosterBoxPro`

3. **Configure Service**
   - **Name**: `boosterboxpro-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for better performance)

4. **Set Environment Variables**
   Same as Railway (see above)

5. **Deploy**
   - Render will build and deploy automatically
   - Copy the generated URL (e.g., `https://boosterboxpro-api.onrender.com`)

---

## 🎨 Step 4: Deploy Frontend (Vercel)

1. **Sign up at [vercel.com](https://vercel.com)**
   - Connect your GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your `BoosterBoxPro` repository
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

3. **Set Environment Variables**
   Go to Settings → Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   (Use your actual backend URL from Step 3)

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Copy the generated URL (e.g., `https://boosterboxpro.vercel.app`)

5. **Set Custom Domain (Optional)**
   - Go to Settings → Domains
   - Add your custom domain (e.g., `boosterboxpro.com`)
   - Update DNS records as instructed

6. **Update Backend CORS**
   - Go back to your backend hosting (Railway/Render)
   - Update `CORS_ORIGINS` environment variable to include your frontend domain:
   ```
   CORS_ORIGINS=https://boosterboxpro.vercel.app,https://boosterboxpro.com,https://www.boosterboxpro.com
   ```
   - Redeploy backend

---

## 🔐 Step 5: Configure Production Environment

### 5.1 Update Database Connection (if needed)

Ensure your `DATABASE_URL` includes SSL:
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db?sslmode=require
```

### 5.2 Generate Production Secrets

**JWT Secret** (if not already set):
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Admin API Key** (if not already set):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5.3 Get Your IP Address

Visit [whatismyipaddress.com](https://whatismyipaddress.com) to get your IP for `ADMIN_ALLOWED_IPS`

---

## 🗄️ Step 6: Database Setup

### 6.1 Run Migrations in Production

**Option A: Via Railway/Render Console**
1. Open your backend service
2. Go to Console/Shell
3. Run:
   ```bash
   alembic upgrade head
   ```

**Option B: Via Local Connection**
1. Connect to production database
2. Run migrations:
   ```bash
   alembic upgrade head
   ```

### 6.2 Verify Database Connection

Test that your backend can connect:
- Check backend logs for "✅ Database connection established"
- If errors, verify `DATABASE_URL` is correct

---

## 🧪 Step 7: Test Deployment

### 7.1 Test Backend API

1. **Health Check**
   ```
   GET https://your-api-url.railway.app/health
   ```
   Should return: `{"status":"healthy"}`

2. **Test Authentication**
   ```
   POST https://your-api-url.railway.app/api/v1/auth/register
   Content-Type: application/json
   
   {
     "email": "test@example.com",
     "password": "Test1234",
     "confirm_password": "Test1234"
   }
   ```

3. **Test Leaderboard (requires auth)**
   ```
   GET https://your-api-url.railway.app/booster-boxes
   Authorization: Bearer YOUR_TOKEN
   ```

### 7.2 Test Frontend

1. **Visit your frontend URL**
   - Should load without errors
   - Check browser console for errors

2. **Test Sign Up**
   - Create a new account
   - Verify email/password validation works

3. **Test Login**
   - Log in with test account
   - Verify redirect to dashboard

4. **Test Dashboard**
   - Should load leaderboard data
   - Verify all metrics display correctly

---

## 🔗 Step 8: Configure Stripe Webhooks (If Using Payments)

1. **Go to Stripe Dashboard**
   - [dashboard.stripe.com](https://dashboard.stripe.com)
   - Switch to **Live mode** (or Test mode for testing)

2. **Create Webhook Endpoint**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `https://your-api-url.railway.app/api/v1/payment/webhook`
   - Select events:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

3. **Copy Webhook Secret**
   - After creating endpoint, click on it
   - Copy "Signing secret" (starts with `whsec_`)
   - Update `STRIPE_WEBHOOK_SECRET` in backend environment variables

4. **Test Webhook**
   - Use Stripe CLI or test a payment
   - Check backend logs for webhook events

---

## ✅ Step 9: Final Verification

### 9.1 Security Checklist

- [ ] `ENVIRONMENT=production` is set
- [ ] `CORS_ORIGINS` includes only your frontend domain(s)
- [ ] `JWT_SECRET_KEY` is long and random (64+ characters)
- [ ] `ADMIN_ALLOWED_IPS` is set to your IP(s)
- [ ] Database connection uses SSL (`sslmode=require`)
- [ ] All API keys are production keys (not test keys)
- [ ] `.env` file is NOT committed to git

### 9.2 Functionality Checklist

- [ ] Homepage loads without errors
- [ ] User can sign up
- [ ] User can log in
- [ ] Dashboard loads with data
- [ ] Leaderboard displays correctly
- [ ] Box detail pages work
- [ ] Admin endpoints are protected
- [ ] Stripe checkout works (if using payments)
- [ ] Webhooks are receiving events

### 9.3 Performance Checklist

- [ ] API responses are fast (< 1 second)
- [ ] Frontend loads quickly
- [ ] Images load correctly
- [ ] No console errors in browser
- [ ] Mobile responsiveness works

---

## 🚨 Troubleshooting

### Backend Won't Start

**Error: "Database connection failed"**
- Check `DATABASE_URL` is correct
- Verify database is accessible from hosting provider
- Check if SSL is required (`?sslmode=require`)

**Error: "Module not found"**
- Verify `requirements.txt` includes all dependencies
- Check build logs for missing packages

**Error: "Port already in use"**
- Ensure using `$PORT` environment variable
- Railway/Render provide this automatically

### Frontend Build Fails

**Error: "Module not found"**
- Run `npm install` locally to verify dependencies
- Check `package.json` is correct

**Error: "API URL not found"**
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Rebuild after setting environment variables

### CORS Errors

**Error: "CORS policy blocked"**
- Verify `CORS_ORIGINS` includes your frontend domain
- Check for trailing slashes (should be no trailing slash)
- Include both `www` and non-`www` versions if using both

### Authentication Issues

**Error: "Not authenticated"**
- Verify JWT secret is set correctly
- Check token is being sent in Authorization header
- Verify token hasn't expired

---

## 📊 Monitoring & Maintenance

### Set Up Error Monitoring (Recommended)

1. **Sentry** (Error Tracking)
   - Sign up at [sentry.io](https://sentry.io)
   - Add to both backend and frontend
   - Get alerts for errors

2. **Uptime Monitoring**
   - Use [UptimeRobot](https://uptimerobot.com) (free)
   - Monitor API health endpoint
   - Get alerts if service goes down

### Regular Maintenance

- **Weekly**: Check error logs
- **Monthly**: Review and update dependencies
- **Quarterly**: Security audit
- **As needed**: Update environment variables

---

## 🔄 Updating Deployment

### Backend Updates

1. Push changes to GitHub
2. Railway/Render will auto-deploy
3. Monitor deployment logs
4. Test endpoints after deployment

### Frontend Updates

1. Push changes to GitHub
2. Vercel will auto-deploy
3. Monitor build logs
4. Test frontend after deployment

### Environment Variable Updates

1. Update in hosting platform dashboard
2. Restart service (usually automatic)
3. Verify changes took effect

---

## 📝 Quick Reference: All Environment Variables

### Backend (Railway/Render)

```bash
# === REQUIRED ===
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db?sslmode=require
ENVIRONMENT=production
JWT_SECRET_KEY=<64+ character random string>
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# === SECURITY ===
ADMIN_ALLOWED_IPS=<your-ip>,<your-other-ip>
ADMIN_IP_ALLOWLIST_ENABLED=true
ADMIN_API_KEY=<random string>

# === PAYMENTS ===
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PRO_PLUS=price_xxx

# === INTEGRATIONS ===
APIFY_API_TOKEN=apify_api_xxx
```

### Frontend (Vercel)

```bash
# === REQUIRED ===
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## 🎉 Success!

Once all steps are complete, your application should be live and accessible!

**Next Steps:**
1. Share your URL with test users
2. Monitor for errors
3. Gather feedback
4. Iterate and improve

---

**Need Help?**
- Check backend logs in Railway/Render dashboard
- Check frontend build logs in Vercel dashboard
- Review error messages carefully
- Test endpoints individually

**Good luck with your launch! 🚀**
