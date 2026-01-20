# Stripe Setup Guide

This guide will help you set up Stripe for the signup and subscription flow.

## Prerequisites

1. A Stripe account (sign up at https://stripe.com)
2. Access to your Stripe Dashboard

## Step 1: Get Your API Keys

1. Go to https://dashboard.stripe.com/test/apikeys (for testing) or https://dashboard.stripe.com/apikeys (for production)
2. Copy your **Publishable Key** and **Secret Key**
3. Add them to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Your secret key
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Your publishable key (for frontend if needed)
STRIPE_WEBHOOK_SECRET=whsec_...  # Will be set after webhook setup (Step 4)
```

## Step 2: Create Subscription Products and Prices

1. Go to https://dashboard.stripe.com/test/products (or /products for production)
2. Create three products:

### Free Tier
- **Name**: Free Plan
- **Type**: Service
- **Price**: $0/month (or create as non-recurring)
- Copy the **Price ID** (looks like `price_xxxxx`)
- Add to `.env`: `STRIPE_PRICE_ID_FREE=price_xxxxx`

### Premium Tier (Recommended)
- **Name**: Premium Plan
- **Type**: Service
- **Price**: $29/month (recurring monthly)
- Copy the **Price ID**
- Add to `.env`: `STRIPE_PRICE_ID_PREMIUM=price_xxxxx`

### Pro Tier
- **Name**: Pro Plan
- **Type**: Service
- **Price**: $79/month (recurring monthly)
- Copy the **Price ID**
- Add to `.env`: `STRIPE_PRICE_ID_PRO=price_xxxxx`

## Step 3: Configure Trial Period

The checkout session is configured to use a 7-day trial period. When creating the checkout session, Stripe will:
- Collect payment method (card)
- Start subscription immediately
- Begin trial period for 7 days
- Charge after trial ends

The trial period is configured in `app/routers/payment.py`:
```python
subscription_data={
    "trial_period_days": request.trial_days,  # 7 days
    "trial_settings": {
        "end_behavior": {
            "missing_payment_method": "cancel",  # Cancel if no payment method
        }
    }
}
```

## Step 4: Set Up Webhook Endpoint

Webhooks allow Stripe to notify your backend when subscription events occur (payment succeeded, failed, cancelled, etc.).

### For Development (Using Stripe CLI)

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks to local server:
   ```bash
   stripe listen --forward-to localhost:8000/payment/webhook
   ```
4. Copy the webhook signing secret (starts with `whsec_`) and add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### For Production

1. Go to https://dashboard.stripe.com/test/webhooks (or /webhooks for production)
2. Click "Add endpoint"
3. Enter your endpoint URL: `https://your-domain.com/payment/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook signing secret and add to `.env`

## Step 5: Update Environment Variables

Add all Stripe configuration to your `.env` file:

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Stripe Price IDs
STRIPE_PRICE_ID_FREE=price_xxxxx
STRIPE_PRICE_ID_PREMIUM=price_xxxxx
STRIPE_PRICE_ID_PRO=price_xxxxx

# Frontend URL (for redirects)
FRONTEND_URL=http://localhost:3000  # For development
# FRONTEND_URL=https://your-domain.com  # For production
```

## Step 6: Test the Flow

1. Start your backend server:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --port 8000
   ```

2. Start your frontend:
   ```bash
   cd frontend && npm run dev
   ```

3. Navigate to `/signup`
4. Fill out the signup form
5. Select a plan (Free, Premium, or Pro)
6. Submit the form
7. You should be redirected to Stripe Checkout
8. Use test card: `4242 4242 4242 4242` (any future expiry, any CVC)
9. Complete checkout
10. You should be redirected back to `/dashboard` with subscription active

## Test Cards

For testing, use these Stripe test cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0027 6000 3184`

Use any future expiry date and any 3-digit CVC.

## Next Steps

After setting up Stripe:

1. **Implement subscription status checking** in your dashboard to verify user has active subscription
2. **Implement paywall** that redirects to signup/payment if subscription is not active
3. **Store subscription data** in your database (user_id, subscription_id, status, trial_end, etc.)
4. **Handle webhook events** to update subscription status in database
5. **Add subscription management** page where users can cancel/update their subscription

## Troubleshooting

- **"Stripe is not configured"**: Check that `STRIPE_SECRET_KEY` is set in `.env`
- **"No Stripe price ID configured"**: Ensure price IDs are set in `.env` for all tiers
- **Webhook verification fails**: Make sure `STRIPE_WEBHOOK_SECRET` matches your webhook endpoint secret
- **Checkout redirects to wrong URL**: Update `FRONTEND_URL` in `.env` to match your frontend URL

