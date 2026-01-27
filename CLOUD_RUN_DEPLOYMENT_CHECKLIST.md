# ✅ Google Cloud Run Deployment Checklist

> **Follow this checklist step-by-step to deploy BoosterBoxPro**

---

## 📋 Pre-Deployment (5 minutes)

- [ ] **Google Cloud account created**
  - Go to [cloud.google.com](https://cloud.google.com)
  - Sign up (free, requires credit card but won't charge)
  - Get $300 free credits

- [ ] **Files ready** ✅
  - [x] Dockerfile created
  - [x] .dockerignore created
  - [x] requirements.txt exists
  - [x] main.py exists

- [ ] **Environment variables prepared**
  - Copy from `.env` file
  - Update `CORS_ORIGINS` with your frontend URL
  - Update `ADMIN_ALLOWED_IPS` with your IP address

---

## 🚀 Deployment Steps (20-30 minutes)

### Step 1: Create Project (2 minutes)

- [ ] Go to [console.cloud.google.com](https://console.cloud.google.com)
- [ ] Click project dropdown → "New Project"
- [ ] Name: `boosterboxpro`
- [ ] Click "Create"
- [ ] Wait for project creation

### Step 2: Enable APIs (2 minutes)

- [ ] Go to [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
- [ ] Search for "Cloud Run API"
- [ ] Click "Enable"
- [ ] Search for "Cloud Build API"
- [ ] Click "Enable"

### Step 3: Create Cloud Run Service (10 minutes)

- [ ] Go to [console.cloud.google.com/run](https://console.cloud.google.com/run)
- [ ] Click "Create Service"
- [ ] Choose "Deploy one revision from a source repository"
- [ ] Connect GitHub account
- [ ] Select repository: `BoosterBoxPro`
- [ ] Select branch: `main`
- [ ] Build type: Dockerfile
- [ ] Dockerfile location: `/Dockerfile`

### Step 4: Configure Service (5 minutes)

**Basic Settings:**
- [ ] Service name: `boosterboxpro-api`
- [ ] Region: `us-central1` (or closest)
- [ ] Memory: `512 MiB`
- [ ] CPU: `1` (or leave default)
- [ ] Minimum instances: `0`
- [ ] Maximum instances: `10`
- [ ] Timeout: `300` seconds
- [ ] Authentication: **Allow unauthenticated invocations**

### Step 5: Set Environment Variables (5 minutes)

Click "Variables & Secrets" → "Add Variable" for each:

- [ ] `DATABASE_URL` = (from .env)
- [ ] `ENVIRONMENT` = `production`
- [ ] `JWT_SECRET_KEY` = (from .env)
- [ ] `CORS_ORIGINS` = `https://your-frontend.vercel.app` (update with your URL)
- [ ] `STRIPE_SECRET_KEY` = (from .env)
- [ ] `STRIPE_PUBLISHABLE_KEY` = (from .env)
- [ ] `STRIPE_WEBHOOK_SECRET` = (from .env)
- [ ] `STRIPE_PRICE_ID_PRO_PLUS` = (from .env)
- [ ] `APIFY_API_TOKEN` = (from .env)
- [ ] `ADMIN_API_KEY` = (from .env)
- [ ] `ADMIN_ALLOWED_IPS` = `YOUR_IP` (get from [whatismyipaddress.com](https://whatismyipaddress.com))
- [ ] `ADMIN_IP_ALLOWLIST_ENABLED` = `true`

### Step 6: Deploy (5-10 minutes)

- [ ] Click "Create" button
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Copy service URL (e.g., `https://boosterboxpro-api-xxxxx.run.app`)

---

## 🧪 Testing (5 minutes)

- [ ] **Health Check**
  - Visit: `https://your-service-url.run.app/health`
  - Should return: `{"status":"healthy"}`

- [ ] **Test Registration**
  ```bash
  curl -X POST https://your-service-url.run.app/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Test1234","confirm_password":"Test1234"}'
  ```

- [ ] **Check Logs**
  - Go to Cloud Run → Your Service → Logs
  - Verify no errors

---

## 🔗 Integration (10 minutes)

### Update Frontend

- [ ] **Go to Vercel** (or your frontend hosting)
- [ ] **Update environment variable:**
  - `NEXT_PUBLIC_API_URL` = `https://your-cloud-run-url.run.app`
- [ ] **Redeploy frontend**

### Update CORS

- [ ] **Go back to Cloud Run**
- [ ] **Edit service** → "Edit & Deploy New Revision"
- [ ] **Update `CORS_ORIGINS`** to include your frontend URL
- [ ] **Deploy revision**

### Configure Stripe Webhook

- [ ] **Go to Stripe Dashboard**
- [ ] **Create webhook endpoint:**
  - URL: `https://your-cloud-run-url.run.app/api/v1/payment/webhook`
  - Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`
- [ ] **Copy webhook secret**
- [ ] **Update `STRIPE_WEBHOOK_SECRET` in Cloud Run**

---

## ✅ Final Verification

- [ ] Homepage loads
- [ ] User can sign up
- [ ] User can log in
- [ ] Dashboard loads with data
- [ ] API endpoints work
- [ ] No console errors
- [ ] Stripe checkout works (if using payments)

---

## 📊 Monitor Usage

- [ ] **Set up billing alerts** (optional)
  - Go to [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
  - Set budget alerts

- [ ] **Monitor Cloud Run metrics**
  - Check request count
  - Check response times
  - Verify within free tier limits

---

## 🎉 Success!

Your app is now live on Google Cloud Run!

**Service URL:** `https://your-service-url.run.app`

**Estimated Monthly Cost:** $0-3 (depending on traffic)

---

## 📚 Quick Reference

**Service URL:** `https://your-service-url.run.app`  
**Health Check:** `https://your-service-url.run.app/health`  
**Logs:** Cloud Run Console → Your Service → Logs  
**Metrics:** Cloud Run Console → Your Service → Metrics  

---

## 🚨 If Something Goes Wrong

1. **Check Logs** - Cloud Run → Your Service → Logs
2. **Check Build Logs** - Cloud Run → Your Service → Revisions → Build Logs
3. **Verify Environment Variables** - Make sure all are set correctly
4. **Test Locally** - Try running Dockerfile locally first
5. **Review Guide** - Check `GOOGLE_CLOUD_RUN_SETUP.md` for detailed troubleshooting

---

**Ready to deploy?** Follow `QUICK_START_CLOUD_RUN.md` for detailed step-by-step instructions!
