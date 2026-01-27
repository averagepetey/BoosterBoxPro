# 💰 Free Backend Hosting Comparison (2026)

> **Best free options for FastAPI/Python backends**

---

## 🏆 Winner: **Render** (Best Free Tier)

### ✅ Why Render is Best for Free:

1. **True Free Tier Available**
   - Free tier with 750 hours/month (enough for 24/7 operation)
   - Services sleep after 15 minutes of inactivity (wakes on request)
   - Perfect for development and low-traffic production

2. **Easy Setup**
   - GitHub integration
   - Auto-detects Python/FastAPI
   - Simple environment variable management

3. **Good for FastAPI**
   - Native Python support
   - Automatic HTTPS
   - Custom domains (free)

4. **Limitations (Free Tier)**
   - Services sleep after 15 min inactivity (first request takes ~30 seconds)
   - 512 MB RAM
   - Limited CPU
   - No persistent storage (but you're using Supabase, so this is fine)

### 🚀 Render Setup (Free Tier)

**Cost:** $0/month (completely free)

**Steps:**
1. Sign up at [render.com](https://render.com) (free)
2. Connect GitHub
3. Create "Web Service"
4. Select your repo
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Deploy!

**Note:** First request after sleep takes ~30 seconds. For production, consider upgrading to $7/month "Starter" plan (no sleep, better performance).

---

## 🥈 Alternative: **Railway** (Pay-as-you-go)

### Railway Details:

1. **$5 Free Credit Monthly**
   - Not truly free, but $5 credit/month
   - Good for very low-traffic apps
   - Credit runs out quickly if you exceed limits

2. **Pricing**
   - $5/month minimum after credit
   - Pay per GB RAM, vCPU, bandwidth
   - Can get expensive with traffic

3. **Pros**
   - No sleep (always on)
   - Better performance than Render free tier
   - Great developer experience

4. **Cons**
   - Not truly free (costs after $5 credit)
   - Can get expensive with usage

**Verdict:** Good if you have $5-10/month budget. Not truly free.

---

## 🥉 Alternative: **Google Cloud Run** (Free Tier Available)

### Google Cloud Run Details:

1. **Free Tier**
   - **$300 free credits** for new customers (lasts ~2-3 months for small apps)
   - **Always-free tier** includes:
     - 2 million requests/month
     - 360,000 GB-seconds of memory
     - 180,000 vCPU-seconds
     - 1 GiB outbound data transfer/month (North America)
   - **Pay-per-use** after free tier (only charges when processing requests)
   - **Scales to zero** (no cost when idle)

2. **Pros**
   - ✅ Truly free for low traffic (2M requests/month is generous)
   - ✅ Scales to zero (no cost when idle)
   - ✅ Always-on (no sleep, instant response)
   - ✅ Excellent performance
   - ✅ Global edge deployment
   - ✅ Auto-scaling
   - ✅ Native FastAPI support

3. **Cons**
   - ⚠️ More complex setup (requires Docker/Cloud Build)
   - ⚠️ Requires Google Cloud account setup
   - ⚠️ Need to understand GCP billing
   - ⚠️ Can get expensive if you exceed free tier

4. **Pricing After Free Tier**
   - ~$0.40 per million requests
   - ~$0.0000025 per GB-second of memory
   - ~$0.0000100 per vCPU-second
   - Very cheap for low-medium traffic

**Verdict:** Excellent free tier, but more complex setup. Best if you want always-on with no sleep.

---

## 🥉 Alternative: **Fly.io** (No Free Tier)

### Fly.io Details:

1. **No Free Tier**
   - Used to have free tier, removed in 2024
   - Starts at ~$2-5/month minimum

2. **Best For**
   - Global edge deployment
   - WebSocket applications
   - Low-latency requirements

**Verdict:** Not free, but cheap if you need edge deployment.

---

## 📊 Quick Comparison Table

| Feature | Render (Free) | Google Cloud Run | Railway | Fly.io |
|---------|--------------|------------------|---------|--------|
| **Cost** | $0/month | $0/month (2M requests) | $5/month (after credit) | $2-5/month |
| **Always On** | ❌ (sleeps) | ✅ (scales to zero) | ✅ | ✅ |
| **Free Requests** | Unlimited | 2M/month | Limited | None |
| **RAM** | 512 MB | Configurable | 512 MB+ | 256 MB+ |
| **Setup Difficulty** | ⭐ Easy | ⭐⭐⭐ Complex | ⭐ Easy | ⭐⭐ Medium |
| **FastAPI Support** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Custom Domain** | ✅ Free | ✅ Free | ✅ Free | ✅ Free |
| **HTTPS** | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Auto |
| **Sleep Timeout** | 15 min | None (scales to zero) | None | None |
| **Global Edge** | ❌ | ✅ | ❌ | ✅ |
| **Best For** | Development, low-traffic | Production, always-on | Small production | Global edge |

---

## 🎯 My Recommendation

### For Truly Free & Easy: **Render** ⭐ (Best for Beginners)

**Use Render if:**
- ✅ You want $0/month cost
- ✅ You want the easiest setup
- ✅ You're okay with 15-30 second wake-up time
- ✅ Low to moderate traffic
- ✅ Development or early production

**Upgrade to Render Starter ($7/month) when:**
- You need always-on (no sleep)
- You have regular traffic
- Wake-up time is unacceptable

### For Truly Free & Always-On: **Google Cloud Run** ⭐ (Best for Production)

**Use Google Cloud Run if:**
- ✅ You want $0/month cost with always-on
- ✅ You need instant response (no sleep)
- ✅ You have up to 2M requests/month
- ✅ You're comfortable with Docker/GCP setup
- ✅ You want production-grade infrastructure

**Why Cloud Run is Great:**
- 2 million requests/month free (very generous!)
- Scales to zero (no cost when idle)
- Always-on (no sleep, instant response)
- Global edge deployment
- Excellent performance
- Pay-per-use after free tier (very cheap)

**Setup Complexity:**
- Requires Dockerfile or Cloud Build
- Need to set up Google Cloud account
- More configuration than Render
- But worth it for always-on free tier!

### For Small Budget ($5-10/month): **Railway**

**Use Railway if:**
- ✅ You have $5-10/month budget
- ✅ You need always-on service
- ✅ You want better performance
- ✅ You prefer pay-as-you-go pricing

---

## 🚀 Quick Start: Render (Free)

### Step-by-Step:

1. **Sign Up**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free)

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select `BoosterBoxPro`

3. **Configure**
   ```
   Name: boosterboxpro-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Set Environment Variables**
   - Add all your env vars (see deployment guide)
   - Make sure `ENVIRONMENT=production`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Copy your URL (e.g., `https://boosterboxpro-api.onrender.com`)

6. **Test**
   - Visit: `https://your-url.onrender.com/health`
   - Should return: `{"status":"healthy"}`

### ⚠️ Important Notes:

- **First Request After Sleep:** Takes 15-30 seconds (service wakes up)
- **Subsequent Requests:** Fast (normal speed)
- **Keep-Alive:** Consider using a monitoring service to ping your API every 10 minutes to prevent sleep (optional)

---

## 💡 Tips to Keep Render Free Service Awake

### Option 1: Uptime Monitoring (Free)
- Use [UptimeRobot](https://uptimerobot.com) (free tier)
- Set up monitor to ping `/health` every 5 minutes
- Keeps service awake 24/7

### Option 2: Cron Job (If you have a server)
- Set up cron to curl your health endpoint every 10 minutes
- Keeps service from sleeping

### Option 3: Accept Sleep (Recommended for Free)
- Let it sleep when not in use
- First request wakes it up
- Saves resources, still free

---

## 📈 When to Upgrade

### Upgrade to Render Starter ($7/month) when:
- ✅ You have regular users (not just testing)
- ✅ 30-second wake-up is unacceptable
- ✅ You need consistent performance
- ✅ You're making revenue

### Upgrade to Railway ($5-10/month) when:
- ✅ You need more control
- ✅ You have variable traffic patterns
- ✅ You want pay-as-you-go pricing

---

## ✅ Final Recommendation

### 🏆 **Best Overall: Google Cloud Run** (If you can handle setup)

**Why Cloud Run Wins:**
- ✅ $0/month with 2M requests/month (very generous!)
- ✅ Always-on (no sleep, instant response)
- ✅ Scales to zero (no cost when idle)
- ✅ Production-grade infrastructure
- ✅ Global edge deployment
- ✅ Very cheap after free tier (~$0.40 per million requests)

**Use Cloud Run if:**
- You want always-on for free
- You're comfortable with Docker/GCP
- You want production-grade from day one
- You have up to 2M requests/month

### 🥈 **Easiest Setup: Render** (Best for Beginners)

**Why Render is Great:**
- ✅ $0/month
- ✅ Easiest setup (5 minutes)
- ✅ Perfect for development
- ✅ No Docker needed

**Use Render if:**
- You want the easiest setup
- You're okay with 15-30 second wake-up
- You're just getting started
- You want to deploy quickly

### 🥉 **Small Budget: Railway** ($5-10/month)

**Use Railway if:**
- You have $5-10/month budget
- You need always-on service
- You want simple setup
- You prefer pay-as-you-go

---

## 🎯 **My Top Pick: Google Cloud Run**

**For a production app, Cloud Run is the best choice:**
1. **Always-on for free** (no sleep like Render)
2. **2M requests/month** is very generous
3. **Scales to zero** (no cost when idle)
4. **Production-grade** infrastructure
5. **Very cheap** after free tier

**The only downside:** Setup is more complex (requires Dockerfile), but it's worth it for always-on free hosting!

---

## 🎯 Action Plan

1. **Start with Render Free** (completely free)
2. **Test your deployment** (make sure everything works)
3. **Monitor usage** (check if sleep is an issue)
4. **Upgrade when needed** (if wake-up time becomes a problem)

**Bottom Line:** Render free tier is the best option for truly free hosting. It's perfect for getting started, and you can always upgrade later!

---

**Questions?** Check the main deployment guide: `PRODUCTION_DEPLOYMENT_GUIDE.md`
