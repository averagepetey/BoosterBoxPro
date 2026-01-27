# 📋 Render Environment Variables - Quick Copy

> **Copy and paste these into Render dashboard**

---

## 🔐 All Environment Variables for Render

Copy each one into Render's "Environment Variables" section:

---

### 1. Database
```
DATABASE_URL=postgresql+asyncpg://user:YOUR_PASSWORD@your-supabase-host:5432/postgres?sslmode=require
```

### 2. Environment
```
ENVIRONMENT=production
```

### 3. JWT Secret
```
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 4. CORS Origins
```
CORS_ORIGINS=https://your-frontend.vercel.app
```
⚠️ **Update this with your actual frontend URL after deploying**

### 5. Stripe Secret Key
```
STRIPE_SECRET_KEY=sk_test_YOUR_STRIPE_SECRET_KEY
```

### 6. Stripe Publishable Key
```
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

### 7. Stripe Webhook Secret
```
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 8. Stripe Price ID
```
STRIPE_PRICE_ID_PRO_PLUS=price_1StEqdKDTumXT1F1ft6PlwAP
```

### 9. Apify API Token
```
APIFY_API_TOKEN=your_apify_api_token_here
```

### 10. Admin API Key
```
Name: ADMIN_API_KEY
Value: [GENERATED_BELOW]
```

### 11. Admin Allowed IPs
```
Name: ADMIN_ALLOWED_IPS
Value: [YOUR_IP_BELOW]
```
⚠️ **Your IP address is shown below**

### 12. Admin IP Allowlist Enabled
```
ADMIN_IP_ALLOWLIST_ENABLED=true
```

---

## ✅ Checklist

- [ ] All 12 variables added
- [ ] `CORS_ORIGINS` updated with frontend URL (after frontend is deployed)
- [ ] `ADMIN_ALLOWED_IPS` updated with your IP address
- [ ] `ENVIRONMENT` set to `production`

---

## 🚀 Quick Deploy Settings

**Service Configuration:**
- **Name**: `boosterboxpro-api`
- **Region**: `Oregon (US West)` or closest
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free`

---

**Ready to deploy!** Follow `RENDER_DEPLOYMENT_GUIDE.md` for step-by-step instructions.
