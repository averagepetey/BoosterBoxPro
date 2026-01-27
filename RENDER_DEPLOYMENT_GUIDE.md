# 🚀 Render Deployment Guide - Step by Step

> **Deploy BoosterBoxPro to Render Free Tier in 10 minutes**

---

## ✅ Pre-Deployment Checklist

- [x] Dockerfile created (for future use)
- [x] Procfile created ✅
- [x] requirements.txt exists ✅
- [x] main.py exists ✅
- [ ] Render account created
- [ ] GitHub repo ready

---

## 📝 Step 1: Create Render Account (2 minutes)

1. **Go to [render.com](https://render.com)**
2. **Click "Get Started for Free"** or "Sign Up"
3. **Sign up with GitHub** (recommended - easiest)
   - Click "Continue with GitHub"
   - Authorize Render to access your GitHub account
   - Select which repositories to allow (choose `BoosterBoxPro`)

**No credit card required!** ✅

---

## 🚀 Step 2: Create Web Service (5 minutes)

### 2.1 Navigate to Dashboard

1. **After signing up**, you'll be on the Render dashboard
2. **Click the blue "New +" button** (top right)
3. **Select "Web Service"**

### 2.2 Connect Repository

1. **You'll see "Connect a repository"**
2. **If GitHub is connected:**
   - You'll see a list of your repositories
   - **Select `BoosterBoxPro`** (or search for it)
   - Click "Connect"

3. **If GitHub is not connected:**
   - Click "Connect account" or "Connect GitHub"
   - Authorize Render
   - Select `BoosterBoxPro` repository
   - Click "Connect"

### 2.3 Configure Service

Fill in these settings:

**Basic Settings:**
- **Name**: `boosterboxpro-api`
- **Region**: `Oregon (US West)` or closest to you
- **Branch**: `main` (or `master` if that's your default)
- **Root Directory**: Leave empty (root of repo)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- **Select: "Free"** (for now, upgrade later if needed)

**Advanced Settings (Click to expand):**
- **Auto-Deploy**: `Yes` (deploys on every push to main)
- **Health Check Path**: `/health` (optional but recommended)

---

## 🔐 Step 3: Set Environment Variables (5 minutes)

### 3.1 Add Variables

**Before clicking "Create Web Service"**, scroll down to **"Environment Variables"** section.

**Click "Add Environment Variable"** for each one:

### 3.2 Required Variables

Add these one by one (copy from your `.env` file):

```
Name: DATABASE_URL
Value: postgresql+asyncpg://postgres.umjtdtksqxtyqeqddwkv:Chessmoves4321!@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```

```
Name: ENVIRONMENT
Value: production
```

```
Name: JWT_SECRET_KEY
Value: tXbFlD96NTtBs52ZaIataOYNODXuUPJKksSeerKkDiEm4G0QKF1DkTE3NaxfIHO05ZFRFkroNd7NqNiatygSCQ
```

```
Name: CORS_ORIGINS
Value: https://your-frontend.vercel.app
```
⚠️ **Update this with your actual frontend URL later, or use placeholder for now**

```
Name: STRIPE_SECRET_KEY
Value: sk_test_YOUR_STRIPE_SECRET_KEY
```

```
Name: STRIPE_PUBLISHABLE_KEY
Value: pk_test_51SkEyEKDTumXT1F1xwjypV989kCNsNxCvoP9VHGJuwCwjAuAFgLaynW4iD3i3ZCasOqxZa0GnwvdRWjbfwzpB3QP00bG10AvUd
```

```
Name: STRIPE_WEBHOOK_SECRET
Value: whsec_05ad1b0fb9ff06782e93c4a5dd99311dad8c9fb0604d8b0106ba83b902ad2f92
```

```
Name: STRIPE_PRICE_ID_PRO_PLUS
Value: price_1StEqdKDTumXT1F1ft6PlwAP
```

```
Name: APIFY_API_TOKEN
Value: your_apify_api_token_here
```

```
Name: ADMIN_API_KEY
Value: your-secret-api-key-here
```

```
Name: ADMIN_ALLOWED_IPS
Value: YOUR_IP_ADDRESS
```
⚠️ **Get your IP from [whatismyipaddress.com](https://whatismyipaddress.com)**

```
Name: ADMIN_IP_ALLOWLIST_ENABLED
Value: true
```

### 3.3 Verify All Variables

Make sure you added all 12 variables before proceeding!

---

## 🚀 Step 4: Deploy (5-10 minutes)

1. **Scroll to bottom of page**
2. **Click "Create Web Service"** (blue button)
3. **Wait for deployment:**
   - Render will:
     - Clone your repo
     - Install dependencies (`pip install -r requirements.txt`)
     - Start your service
   - This takes 5-10 minutes
   - You'll see build logs in real-time

4. **When complete:**
   - You'll see "Live" status
   - Your service URL will be shown (e.g., `https://boosterboxpro-api.onrender.com`)
   - **Copy this URL!** You'll need it for frontend

---

## 🧪 Step 5: Test Deployment (2 minutes)

### 5.1 Health Check

Open your browser and visit:
```
https://your-service-name.onrender.com/health
```

Should return: `{"status":"healthy"}`

### 5.2 Test API

Test registration endpoint:
```bash
curl -X POST https://your-service-name.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'
```

### 5.3 Check Logs

1. **In Render dashboard**, click on your service
2. **Click "Logs" tab**
3. **Verify no errors**
4. **Look for:** "Application startup complete" or similar

---

## 🔗 Step 6: Update Frontend (5 minutes)

### 6.1 Update API URL in Vercel

1. **Go to [vercel.com](https://vercel.com)**
2. **Select your project**
3. **Go to Settings → Environment Variables**
4. **Update or add:**
   ```
   NEXT_PUBLIC_API_URL=https://your-service-name.onrender.com
   ```
5. **Redeploy frontend** (or it will auto-deploy if connected to GitHub)

### 6.2 Update CORS in Render

1. **Go back to Render dashboard**
2. **Click on your service**
3. **Go to "Environment" tab**
4. **Find `CORS_ORIGINS` variable**
5. **Click "Edit"**
6. **Update value to include your frontend URL:**
   ```
   https://your-frontend.vercel.app,https://yourdomain.com
   ```
7. **Click "Save Changes"**
8. **Service will automatically redeploy**

---

## 💡 Step 7: Keep Service Awake (Free - Recommended)

### Set Up UptimeRobot (5 minutes)

1. **Go to [uptimerobot.com](https://uptimerobot.com)**
2. **Sign up** (free account)
3. **Click "Add New Monitor"**
4. **Configure:**
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: BoosterBoxPro API
   - **URL**: `https://your-service-name.onrender.com/health`
   - **Monitoring Interval**: 5 minutes
   - **Alert Contacts**: Your email (optional)
5. **Click "Create Monitor"**

**Result:** Service stays awake 24/7, no sleep delays! ✅

---

## 🔧 Step 8: Configure Stripe Webhook (If Using Payments)

1. **Go to Stripe Dashboard**
   - [dashboard.stripe.com](https://dashboard.stripe.com)
   - Switch to **Test mode** (or Live mode for production)

2. **Create Webhook**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - **Endpoint URL**: `https://your-service-name.onrender.com/api/v1/payment/webhook`
   - **Events to send**:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

3. **Copy Webhook Secret**
   - After creating, click on the endpoint
   - Copy "Signing secret" (starts with `whsec_`)
   - Update `STRIPE_WEBHOOK_SECRET` in Render environment variables

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] Web service created
- [ ] Repository connected
- [ ] All environment variables set (12 variables)
- [ ] Service deployed successfully
- [ ] Health endpoint works (`/health`)
- [ ] API endpoints tested
- [ ] Logs checked (no errors)
- [ ] Frontend updated with new API URL
- [ ] CORS updated with frontend URL
- [ ] UptimeRobot set up (keeps service awake)
- [ ] Stripe webhook configured (if using payments)

---

## 🚨 Troubleshooting

### Service Won't Start

**Check logs:**
1. Go to Render dashboard → Your Service → Logs
2. Look for errors
3. Common issues:
   - **"Module not found"** → Check requirements.txt
   - **"Port not found"** → Verify start command uses `$PORT`
   - **"Database connection failed"** → Check `DATABASE_URL`

### Build Fails

**Common causes:**
- Missing dependencies in requirements.txt
- Python version mismatch
- Build command incorrect

**Fix:**
- Check build logs in Render
- Verify requirements.txt is complete
- Ensure build command is: `pip install -r requirements.txt`

### Service Sleeps (30-second delay)

**Solution:**
- Set up UptimeRobot (see Step 7)
- Or upgrade to Starter plan ($7/month) for always-on

### CORS Errors

**Fix:**
- Update `CORS_ORIGINS` in Render environment variables
- Include your frontend URL (no trailing slash)
- Include both `www` and non-`www` versions if using both
- Redeploy service after updating

### Database Connection Issues

**Check:**
- `DATABASE_URL` is correct
- Supabase allows connections from Render IPs
- SSL is enabled (`?sslmode=require`)

---

## 📊 Monitor Your Service

### View Logs:
- Render Dashboard → Your Service → Logs
- Real-time logs
- Search and filter logs

### View Metrics:
- Render Dashboard → Your Service → Metrics
- Request count
- Response times
- Error rates

### Set Up Alerts:
- Render Dashboard → Your Service → Alerts
- Get notified of errors or downtime

---

## 🔄 Updating Your Service

### Automatic Deploys:
- Render auto-deploys on every push to `main` branch
- No manual action needed

### Manual Deploy:
1. Go to Render Dashboard → Your Service
2. Click "Manual Deploy"
3. Select branch/commit
4. Click "Deploy"

### Update Environment Variables:
1. Go to Render Dashboard → Your Service
2. Go to "Environment" tab
3. Click "Edit" on any variable
4. Update value
5. Click "Save Changes"
6. Service will automatically redeploy

---

## 💰 Understanding Costs

### Free Tier:
- ✅ $0/month
- ✅ 750 hours/month (enough for 24/7)
- ✅ Unlimited requests
- ⚠️ Service sleeps after 15 min inactivity

### Starter Plan ($7/month):
- ✅ Always-on (no sleep)
- ✅ Better performance
- ✅ More resources
- ✅ Priority support

**Upgrade when:**
- You have 500+ active users
- You're making revenue
- Sleep delays are unacceptable

---

## 🎉 Success!

Your FastAPI app is now live on Render!

**Service URL:** `https://your-service-name.onrender.com`

**Next Steps:**
1. ✅ Test all endpoints
2. ✅ Update frontend with new API URL
3. ✅ Set up UptimeRobot (keep service awake)
4. ✅ Configure Stripe webhook
5. ✅ Monitor usage and performance

---

## 📚 Quick Reference

**Service URL:** `https://your-service-name.onrender.com`  
**Health Check:** `https://your-service-name.onrender.com/health`  
**Logs:** Render Dashboard → Your Service → Logs  
**Environment Variables:** Render Dashboard → Your Service → Environment  
**Metrics:** Render Dashboard → Your Service → Metrics  

---

## 🆘 Need Help?

- **Render Docs:** [render.com/docs](https://render.com/docs)
- **Render Support:** [render.com/support](https://render.com/support)
- **Check Logs:** Always check logs first for errors
- **Community:** [community.render.com](https://community.render.com)

---

**Ready to deploy?** Follow the steps above, and you'll be live in 10 minutes! 🚀
