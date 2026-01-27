# 🚀 Quick Start: Deploy to Google Cloud Run

> **Step-by-step guide to deploy BoosterBoxPro in 30 minutes**

---

## ✅ Pre-Deployment Checklist

- [x] Dockerfile created ✅
- [x] .dockerignore created ✅
- [x] requirements.txt exists ✅
- [ ] Google Cloud account created
- [ ] Environment variables ready

---

## 📝 Step 1: Create Google Cloud Account

1. **Go to [cloud.google.com](https://cloud.google.com)**
2. **Sign up** (free, requires credit card but won't charge unless you exceed free tier)
3. **Get $300 free credits** (lasts 90 days, more than enough to test)

---

## 🌐 Step 2: Create Cloud Run Service (Console Method)

### 2.1 Navigate to Cloud Run

1. Go to [console.cloud.google.com/run](https://console.cloud.google.com/run)
2. **Select or create a project**
   - Click project dropdown at top
   - Click "New Project"
   - Name: `boosterboxpro` (or your choice)
   - Click "Create"

### 2.2 Create Service

1. Click **"Create Service"** button
2. Choose **"Deploy one revision from a source repository"**
   - This will build from your GitHub repo automatically

### 2.3 Connect GitHub (if using source)

1. **Authorize Google Cloud** to access GitHub
2. **Select repository**: `BoosterBoxPro`
3. **Select branch**: `main`
4. **Build type**: Dockerfile
5. **Dockerfile location**: `/Dockerfile` (root of repo)

### 2.4 Configure Service

**Basic Settings:**
- **Service name**: `boosterboxpro-api`
- **Region**: `us-central1` (or closest to you)
- **CPU allocation**: CPU is only allocated during request processing
- **Memory**: `512 MiB` (or `1 GiB` if needed)
- **Minimum instances**: `0` (scales to zero - free when idle)
- **Maximum instances**: `10` (or more if needed)
- **Request timeout**: `300` seconds (5 minutes)

**Container Settings:**
- **Container port**: `8080`
- **Authentication**: **Allow unauthenticated invocations** (for public API)

### 2.5 Set Environment Variables

Click **"Variables & Secrets"** tab, then **"Add Variable"** for each:

```bash
DATABASE_URL=postgresql+asyncpg://postgres.umjtdtksqxtyqeqddwkv:Chessmoves4321!@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
ENVIRONMENT=production
JWT_SECRET_KEY=tXbFlD96NTtBs52ZaIataOYNODXuUPJKksSeerKkDiEm4G0QKF1DkTE3NaxfIHO05ZFRFkroNd7NqNiatygSCQ
CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
STRIPE_SECRET_KEY=sk_test_YOUR_STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_51SkEyEKDTumXT1F1xwjypV989kCNsNxCvoP9VHGJuwCwjAuAFgLaynW4iD3i3ZCasOqxZa0GnwvdRWjbfwzpB3QP00bG10AvUd
STRIPE_WEBHOOK_SECRET=whsec_05ad1b0fb9ff06782e93c4a5dd99311dad8c9fb0604d8b0106ba83b902ad2f92
STRIPE_PRICE_ID_PRO_PLUS=price_1StEqdKDTumXT1F1ft6PlwAP
APIFY_API_TOKEN=your_apify_api_token_here
ADMIN_API_KEY=your-secret-api-key-here
ADMIN_ALLOWED_IPS=YOUR_IP_ADDRESS
ADMIN_IP_ALLOWLIST_ENABLED=true
```

**⚠️ Important:**
- Replace `CORS_ORIGINS` with your actual frontend URL (or use placeholder for now)
- Replace `ADMIN_ALLOWED_IPS` with your IP (get from [whatismyipaddress.com](https://whatismyipaddress.com))
- For production, use `sk_live_` Stripe keys (not `sk_test_`)

### 2.6 Deploy

1. Click **"Create"** button
2. Wait 5-10 minutes for build and deployment
3. Copy your service URL (e.g., `https://boosterboxpro-api-xxxxx.run.app`)

---

## 🧪 Step 3: Test Deployment

### 3.1 Health Check

Open your browser or use curl:
```
https://your-service-url.run.app/health
```

Should return: `{"status":"healthy"}`

### 3.2 Test API Endpoint

Test registration:
```bash
curl -X POST https://your-service-url.run.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'
```

Should return user data or validation error.

---

## 🔧 Step 4: Update Frontend

### 4.1 Update API URL

In your frontend deployment (Vercel), update environment variable:

```
NEXT_PUBLIC_API_URL=https://your-cloud-run-url.run.app
```

### 4.2 Update CORS

Go back to Cloud Run service:
1. Click "Edit & Deploy New Revision"
2. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
   ```
3. Click "Deploy"

---

## 🔐 Step 5: Configure Stripe Webhook

1. **Go to Stripe Dashboard**
   - [dashboard.stripe.com](https://dashboard.stripe.com)
   - Switch to **Live mode** (or Test mode for testing)

2. **Create Webhook**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `https://your-cloud-run-url.run.app/api/v1/payment/webhook`
   - Select events:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

3. **Copy Webhook Secret**
   - After creating, click on the endpoint
   - Copy "Signing secret" (starts with `whsec_`)
   - Update `STRIPE_WEBHOOK_SECRET` in Cloud Run environment variables

---

## 📊 Step 6: Monitor & Verify

### 6.1 Check Logs

1. Go to Cloud Run console
2. Click on your service
3. Click "Logs" tab
4. Verify no errors

### 6.2 Check Metrics

1. Click "Metrics" tab
2. Verify requests are coming through
3. Check response times

### 6.3 Test Full Flow

- [ ] Homepage loads
- [ ] User can sign up
- [ ] User can log in
- [ ] Dashboard loads with data
- [ ] API endpoints work
- [ ] Stripe checkout works (if using payments)

---

## 💰 Step 7: Understand Billing

### Free Tier (Always Free):
- ✅ 2 million requests/month
- ✅ 360,000 GB-seconds of memory
- ✅ 180,000 vCPU-seconds
- ✅ 1 GiB outbound data transfer/month (North America)

### After Free Tier:
- ~$0.40 per million requests
- Very cheap for most apps

### Monitor Usage:
1. Go to [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
2. Set up billing alerts (optional)
3. Monitor usage in Cloud Run metrics

---

## 🚨 Troubleshooting

### Service Won't Start

**Check logs:**
1. Go to Cloud Run → Your Service → Logs
2. Look for errors
3. Common issues:
   - Database connection failed → Check `DATABASE_URL`
   - Port not found → Verify Dockerfile uses `${PORT}`
   - Module not found → Check requirements.txt

### Database Connection Issues

**Error: "Database connection failed"**
- Verify `DATABASE_URL` is correct
- Check if Supabase allows connections from Cloud Run
- Ensure SSL is enabled (`?sslmode=require`)

### CORS Errors

**Error: "CORS policy blocked"**
- Verify `CORS_ORIGINS` includes your frontend domain
- No trailing slashes
- Include both `www` and non-`www` versions

### Build Fails

**Error: "Build failed"**
- Check Dockerfile syntax
- Verify all files are in repo
- Check build logs in Cloud Run console

---

## ✅ Deployment Checklist

- [ ] Google Cloud account created
- [ ] Project created
- [ ] Cloud Run service created
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health endpoint works
- [ ] API endpoints tested
- [ ] Frontend updated with new API URL
- [ ] CORS configured correctly
- [ ] Stripe webhook configured (if using payments)
- [ ] Logs checked for errors
- [ ] Billing alerts set up (optional)

---

## 🎉 Success!

Your FastAPI app is now running on Google Cloud Run!

**Your service URL:** `https://your-service-url.run.app`

**Next Steps:**
1. Update frontend `NEXT_PUBLIC_API_URL`
2. Test all endpoints
3. Monitor usage
4. Set up custom domain (optional)

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI on Cloud Run Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

---

**Need Help?**
- Check Cloud Run logs for errors
- Review `GOOGLE_CLOUD_RUN_SETUP.md` for detailed guide
- Google Cloud support (if on paid plan)
