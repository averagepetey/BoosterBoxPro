# 🔗 How to Connect GitHub Repo to Google Cloud Run

> **Step-by-step guide with screenshots guidance**

---

## 🎯 Quick Steps Overview

1. Navigate to Cloud Run
2. Create Service
3. Connect GitHub
4. Select Repository
5. Configure Build
6. Deploy

---

## 📍 Step 1: Navigate to Cloud Run

### From the Dashboard:

1. **In the left sidebar**, look for "Cloud Run" under "Products"
   - If you don't see it, click "View all products" at the bottom
   - Search for "Cloud Run" in the search bar at the top

2. **OR use the search bar:**
   - Click the search bar at the top (or press `/`)
   - Type: `Cloud Run`
   - Click on "Cloud Run" from the results

3. **You should now see the Cloud Run page**

---

## 🚀 Step 2: Create Service

1. **Click the big blue "CREATE SERVICE" button** (top of the page)

2. **You'll see deployment options:**
   - "Deploy one revision from a source repository" ← **Choose this one**
   - "Deploy a container image" (we'll skip this)

---

## 🔗 Step 3: Connect GitHub Repository

### Option A: First Time Connecting (Recommended)

1. **Click "SET UP WITH CLOUD BUILD"** or "Connect Repository"
   - You'll see options to connect GitHub, Bitbucket, or GitLab

2. **Select "GitHub (Cloud Build GitHub App)"**
   - This is the easiest method

3. **Click "INSTALL CLOUD BUILD GITHUB APP"** or "Connect Repository"
   - This will open a GitHub authorization page

4. **Authorize Google Cloud Build:**
   - You'll be redirected to GitHub
   - Sign in to GitHub if needed
   - Click "Authorize google-cloud-build" or "Install"
   - Select which repositories to allow access:
     - Choose "Only select repositories"
     - Select `BoosterBoxPro` (or your repo name)
   - Click "Install" or "Authorize"

5. **Return to Cloud Run:**
   - You'll be redirected back to Google Cloud Console
   - You should now see your repositories listed

### Option B: If GitHub is Already Connected

1. **You'll see a dropdown with your repositories**
2. **Select `BoosterBoxPro`** (or your repo name)

---

## ⚙️ Step 4: Configure Repository Settings

After selecting your repository, you'll see configuration options:

1. **Repository:**
   - Should show: `your-username/BoosterBoxPro` or similar
   - If not, select it from the dropdown

2. **Branch:**
   - Select: `main` (or `master` if that's your default branch)

3. **Build Type:**
   - Select: **"Dockerfile"** (not "Buildpack")

4. **Dockerfile location:**
   - Enter: `/Dockerfile` (or just `Dockerfile`)
   - This tells Cloud Build where to find your Dockerfile

5. **Docker context:**
   - Leave as `/` (root directory)

---

## 🏷️ Step 5: Configure Service Settings

### Basic Settings Tab:

1. **Service name:**
   - Enter: `boosterboxpro-api`

2. **Region:**
   - Select: `us-central1` (Iowa) or closest to you
   - Other good options: `us-east1`, `us-west1`

3. **Deploy a new revision:**
   - Leave as default (checked)

### Container Tab:

1. **Container port:**
   - Enter: `8080` (Cloud Run default)

2. **CPU allocation:**
   - Select: "CPU is only allocated during request processing" (cheaper)

3. **Memory:**
   - Select: `512 MiB` (or `1 GiB` if you need more)

4. **Minimum instances:**
   - Set to: `0` (scales to zero - free when idle)

5. **Maximum instances:**
   - Set to: `10` (or more if you expect high traffic)

6. **Request timeout:**
   - Set to: `300` seconds (5 minutes)

7. **Concurrency:**
   - Leave default (80 requests per instance)

### Security Tab:

1. **Authentication:**
   - Select: **"Allow unauthenticated invocations"**
   - This makes your API publicly accessible (needed for your frontend)

---

## 🔐 Step 6: Set Environment Variables

1. **Click "Variables & Secrets" tab** (at the top)

2. **Click "ADD VARIABLE"** for each environment variable

3. **Add these variables one by one:**

   ```
   Name: DATABASE_URL
   Value: postgresql+asyncpg://user:YOUR_PASSWORD@your-supabase-host:5432/postgres?sslmode=require
   ```

   ```
   Name: ENVIRONMENT
   Value: production
   ```

   ```
   Name: JWT_SECRET_KEY
   Value: your-jwt-secret-key-here
   ```

   ```
   Name: CORS_ORIGINS
   Value: https://your-frontend.vercel.app
   ```
   (Replace with your actual frontend URL, or use placeholder for now)

   ```
   Name: STRIPE_SECRET_KEY
   Value: sk_test_YOUR_STRIPE_SECRET_KEY
   ```

   ```
   Name: STRIPE_PUBLISHABLE_KEY
   Value: pk_test_your_publishable_key_here
   ```

   ```
   Name: STRIPE_WEBHOOK_SECRET
   Value: whsec_your_webhook_secret_here
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
   (Get your IP from [whatismyipaddress.com](https://whatismyipaddress.com))

   ```
   Name: ADMIN_IP_ALLOWLIST_ENABLED
   Value: true
   ```

---

## 🚀 Step 7: Deploy

1. **Review all settings** (scroll through all tabs)

2. **Click the blue "CREATE" button** at the bottom

3. **Wait for deployment** (5-10 minutes):
   - You'll see build progress
   - Cloud Build will:
     - Clone your repo
     - Build the Docker image
     - Push to Container Registry
     - Deploy to Cloud Run

4. **When complete**, you'll see:
   - ✅ Service deployed successfully
   - Your service URL (e.g., `https://boosterboxpro-api-xxxxx.run.app`)

---

## 🧪 Step 8: Test Your Deployment

1. **Copy your service URL** (shown after deployment)

2. **Test health endpoint:**
   ```
   https://your-service-url.run.app/health
   ```
   Should return: `{"status":"healthy"}`

3. **Check logs:**
   - Click on your service name
   - Go to "Logs" tab
   - Verify no errors

---

## 🚨 Troubleshooting

### "Repository not found" or "Can't connect to GitHub"

**Solution:**
1. Make sure you authorized Cloud Build GitHub App
2. Check that you selected the correct repository in GitHub authorization
3. Try disconnecting and reconnecting:
   - Go to Cloud Build → Settings → Connected repositories
   - Remove connection
   - Reconnect following Step 3

### "Dockerfile not found"

**Solution:**
1. Verify Dockerfile exists in your repo root
2. Check Dockerfile location is set to `/Dockerfile` or `Dockerfile`
3. Make sure you're on the correct branch (`main`)

### "Build failed"

**Solution:**
1. Check build logs:
   - Go to Cloud Run → Your Service → Revisions
   - Click on the revision
   - Click "View logs" or "Build logs"
2. Common issues:
   - Missing dependencies in requirements.txt
   - Dockerfile syntax error
   - Environment variables not set

### "Service won't start"

**Solution:**
1. Check service logs:
   - Cloud Run → Your Service → Logs
2. Common issues:
   - Database connection failed → Check `DATABASE_URL`
   - Port not found → Verify Dockerfile uses `${PORT}`
   - Missing environment variables

---

## ✅ Quick Checklist

- [ ] Navigated to Cloud Run
- [ ] Clicked "CREATE SERVICE"
- [ ] Selected "Deploy from source repository"
- [ ] Connected GitHub account
- [ ] Selected `BoosterBoxPro` repository
- [ ] Selected `main` branch
- [ ] Set build type to "Dockerfile"
- [ ] Set Dockerfile location to `/Dockerfile`
- [ ] Configured service settings (name, region, memory, etc.)
- [ ] Set all environment variables
- [ ] Clicked "CREATE"
- [ ] Waited for deployment (5-10 min)
- [ ] Copied service URL
- [ ] Tested health endpoint

---

## 🎯 What Happens Next

After deployment:

1. **Your service URL** will be something like:
   ```
   https://boosterboxpro-api-xxxxx-uc.a.run.app
   ```

2. **Update your frontend:**
   - Go to Vercel (or your frontend hosting)
   - Update `NEXT_PUBLIC_API_URL` environment variable
   - Set it to your Cloud Run URL

3. **Update CORS:**
   - Go back to Cloud Run
   - Edit service → Update `CORS_ORIGINS` with your frontend URL
   - Deploy new revision

4. **Configure Stripe webhook:**
   - Use your Cloud Run URL for webhook endpoint

---

## 💡 Pro Tips

1. **Save your service URL** - You'll need it for frontend and Stripe
2. **Bookmark Cloud Run page** - Easy access for future updates
3. **Check logs regularly** - Monitor for errors
4. **Set up billing alerts** - Get notified if you exceed free tier

---

**Need more help?** Check `QUICK_START_CLOUD_RUN.md` for the full deployment guide!
