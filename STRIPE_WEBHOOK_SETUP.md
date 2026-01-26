# Stripe Webhook Setup for Local Development

## The Issue
After completing Stripe checkout, the subscription isn't being registered because webhooks aren't being received.

## Solution: Run Stripe CLI

You need to run Stripe CLI to forward webhook events from Stripe to your local backend.

### Step 1: Install Stripe CLI (if not already installed)
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Or download from: https://stripe.com/docs/stripe-cli
```

### Step 2: Login to Stripe CLI
```bash
stripe login
```

### Step 3: Forward Webhooks to Your Backend
Open a **new terminal window** and run:
```bash
stripe listen --forward-to localhost:8000/api/v1/payment/webhook
```

You should see output like:
```
> Ready! Your webhook signing secret is whsec_xxxxx (^C to quit)
```

### Step 4: Update Your .env File
Copy the webhook signing secret from the CLI output and add it to your `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Step 5: Restart Your Backend
After adding the webhook secret, restart your backend server:
```bash
# Stop the current server (Ctrl+C)
# Then restart:
source venv/bin/activate
python main.py
```

## Testing the Flow

1. **Keep Stripe CLI running** in one terminal
2. **Keep backend running** in another terminal  
3. **Start frontend** in a third terminal (if not already running)
4. **Sign up** and complete checkout with test card: `4242 4242 4242 4242`
5. **Watch the Stripe CLI terminal** - you should see webhook events:
   ```
   --> checkout.session.completed [200]
   --> customer.subscription.created [200]
   ```

## What Was Fixed

1. ✅ **Frontend API URL** - Fixed `/payment/verify-subscription/` → `/api/v1/payment/verify-subscription/`
2. ✅ **Subscription Status Check** - Now recognizes `'trial'` status as active access
3. ✅ **Verify Endpoint** - Now updates user subscription even if webhook hasn't processed yet

## Troubleshooting

### Webhook events not showing in Stripe CLI
- Make sure Stripe CLI is running: `stripe listen --forward-to localhost:8000/api/v1/payment/webhook`
- Check that backend is running on port 8000
- Verify `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe CLI

### Still getting "subscription required" error
- Check backend logs for webhook events
- Verify user's `subscription_status` in database (should be 'trial' or 'active')
- Check that `trial_ended_at` is set correctly (7 days from now)

### Payment not showing in Stripe Dashboard
- This is normal for test mode - check Stripe Dashboard → Payments (test mode)
- Make sure you're using test API keys (`sk_test_...`)
- Test payments appear in the test mode section of Stripe Dashboard

---

**Important:** Keep the Stripe CLI running while testing! Webhooks won't work without it.
