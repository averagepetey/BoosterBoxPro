# 🚀 Google Cloud Run Setup Guide

> **Deploy FastAPI to Google Cloud Run (Always-on Free Tier)**

---

## 🎯 Why Google Cloud Run?

- ✅ **$0/month** with 2 million requests/month free
- ✅ **Always-on** (no sleep, instant response)
- ✅ **Scales to zero** (no cost when idle)
- ✅ **Production-grade** infrastructure
- ✅ **Global edge** deployment

---

## 📋 Prerequisites

1. Google Cloud account ([cloud.google.com](https://cloud.google.com))
2. Google Cloud CLI installed (optional, but helpful)
3. Docker installed (for local testing, optional)

---

## 🔧 Step 1: Create Dockerfile

Create `Dockerfile` in your project root:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run sets PORT env var)
EXPOSE 8080

# Run the application
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
```

---

## 🔧 Step 2: Create .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.env
.env.local
.git
.gitignore
*.md
node_modules/
frontend/
.next/
.DS_Store
```

---

## 🌐 Step 3: Deploy to Cloud Run

### Option A: Using Google Cloud Console (Easiest)

1. **Go to Cloud Run**
   - Visit [console.cloud.google.com/run](https://console.cloud.google.com/run)
   - Select or create a project

2. **Create Service**
   - Click "Create Service"
   - Choose "Deploy one revision from a source repository" or "Deploy a container image"

3. **Configure Service**
   - **Service name**: `boosterboxpro-api`
   - **Region**: Choose closest to you (e.g., `us-central1`)
   - **Authentication**: Allow unauthenticated invocations (for public API)
   - **Container**: 
     - If using source: Connect GitHub repo
     - If using image: Upload Docker image

4. **Set Environment Variables**
   - Click "Variables & Secrets"
   - Add all your environment variables:
     ```
     DATABASE_URL=...
     ENVIRONMENT=production
     JWT_SECRET_KEY=...
     CORS_ORIGINS=...
     STRIPE_SECRET_KEY=...
     STRIPE_WEBHOOK_SECRET=...
     APIFY_API_TOKEN=...
     ADMIN_API_KEY=...
     ADMIN_ALLOWED_IPS=...
     ADMIN_IP_ALLOWLIST_ENABLED=true
     ```

5. **Configure Resources**
   - **CPU**: 1 vCPU (free tier allows this)
   - **Memory**: 512 MiB (or 1 GiB if needed)
   - **Min instances**: 0 (scales to zero)
   - **Max instances**: 10 (or more if needed)
   - **Timeout**: 300 seconds (5 minutes)

6. **Deploy**
   - Click "Create"
   - Wait 5-10 minutes for deployment
   - Copy your service URL (e.g., `https://boosterboxpro-api-xxxxx.run.app`)

### Option B: Using gcloud CLI (Advanced)

1. **Install gcloud CLI**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build and Deploy**
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/boosterboxpro-api
   
   # Deploy to Cloud Run
   gcloud run deploy boosterboxpro-api \
     --image gcr.io/YOUR_PROJECT_ID/boosterboxpro-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --timeout 300 \
     --set-env-vars "ENVIRONMENT=production,DATABASE_URL=...,JWT_SECRET_KEY=..."
   ```

---

## 🔐 Step 4: Set Up Environment Variables

### In Cloud Run Console:

1. Go to your service
2. Click "Edit & Deploy New Revision"
3. Go to "Variables & Secrets" tab
4. Add all required variables:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db?sslmode=require
ENVIRONMENT=production
JWT_SECRET_KEY=your-64-char-secret
CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PRO_PLUS=price_xxx
APIFY_API_TOKEN=apify_api_xxx
ADMIN_API_KEY=your-admin-key
ADMIN_ALLOWED_IPS=your-ip
ADMIN_IP_ALLOWLIST_ENABLED=true
```

5. Click "Deploy"

---

## 🧪 Step 5: Test Deployment

1. **Health Check**
   ```bash
   curl https://your-service-url.run.app/health
   ```
   Should return: `{"status":"healthy"}`

2. **Test API**
   ```bash
   curl https://your-service-url.run.app/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test1234","confirm_password":"Test1234"}'
   ```

---

## 💰 Step 6: Understand Free Tier Limits

### Always-Free Tier Includes:
- ✅ **2 million requests/month**
- ✅ **360,000 GB-seconds of memory**
- ✅ **180,000 vCPU-seconds**
- ✅ **1 GiB outbound data transfer/month** (North America)

### After Free Tier (Very Cheap):
- ~$0.40 per million requests
- ~$0.0000025 per GB-second of memory
- ~$0.0000100 per vCPU-second

**Example:** If you use 3M requests/month:
- First 2M: Free
- Next 1M: ~$0.40
- **Total: $0.40/month** (very cheap!)

---

## 🔄 Step 7: Set Up Custom Domain (Optional)

1. **In Cloud Run Console**
   - Go to your service
   - Click "Manage Custom Domains"
   - Add your domain (e.g., `api.boosterboxpro.com`)

2. **Update DNS**
   - Add CNAME record pointing to Cloud Run service
   - Wait for DNS propagation

3. **Update CORS**
   - Update `CORS_ORIGINS` to include your custom domain

---

## 🚨 Troubleshooting

### Service Won't Start

**Error: "Container failed to start"**
- Check Dockerfile is correct
- Verify `main:app` is correct (FastAPI app location)
- Check logs in Cloud Run console

**Error: "Port not found"**
- Ensure using `${PORT}` environment variable
- Cloud Run sets `PORT` automatically

### Database Connection Issues

**Error: "Database connection failed"**
- Verify `DATABASE_URL` is correct
- Check if database allows connections from Cloud Run IPs
- Ensure SSL is enabled (`?sslmode=require`)

### CORS Errors

**Error: "CORS policy blocked"**
- Verify `CORS_ORIGINS` includes your frontend domain
- Check for trailing slashes
- Include both `www` and non-`www` versions

---

## 📊 Monitoring

### View Logs
1. Go to Cloud Run console
2. Click on your service
3. Click "Logs" tab
4. View real-time logs

### Set Up Alerts
1. Go to Cloud Monitoring
2. Create alert for errors
3. Set up email/SMS notifications

---

## 🔄 Continuous Deployment

### Option 1: GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy boosterboxpro-api \
            --source . \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
```

### Option 2: Cloud Build (Automatic)

1. Enable Cloud Build API
2. Connect GitHub repository
3. Cloud Build will auto-deploy on push

---

## ✅ Final Checklist

- [ ] Dockerfile created and tested
- [ ] Service deployed to Cloud Run
- [ ] Environment variables set
- [ ] Health endpoint working
- [ ] API endpoints tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] CORS configured correctly

---

## 🎉 Success!

Your FastAPI app is now running on Google Cloud Run with:
- ✅ Always-on (no sleep)
- ✅ Free tier (2M requests/month)
- ✅ Production-grade infrastructure
- ✅ Global edge deployment

**Next Steps:**
1. Update frontend `NEXT_PUBLIC_API_URL` to your Cloud Run URL
2. Test all endpoints
3. Monitor usage and costs
4. Set up alerts

---

**Need Help?**
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI on Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service)
- Check Cloud Run logs for errors
