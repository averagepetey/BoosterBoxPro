# Stripe Keys Setup Instructions

## ✅ Your Stripe Test Keys

Add these to your `.env` file:

```bash
# Stripe Payment Integration
STRIPE_SECRET_KEY=sk_test_xxxxx  # Get from Stripe Dashboard -> Developers -> API keys
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx  # Get from Stripe Dashboard -> Developers -> API keys
```

## Next Steps

### 1. Create Products & Prices in Stripe Dashboard

1. Go to [Stripe Dashboard → Products](https://dashboard.stripe.com/test/products)
2. Click "Add product"
3. Create two products:
   - **Premium Plan** (e.g., $29/month)
   - **Pro Plan** (e.g., $79/month)
4. For each product:
   - Set up as "Recurring" subscription
   - Choose billing period (monthly recommended)
   - Set the price
   - Save and copy the **Price ID** (starts with `price_`)
5. Add Price IDs to `.env`:
   ```bash
   STRIPE_PRICE_ID_PREMIUM=price_xxxxx
   STRIPE_PRICE_ID_PRO=price_xxxxx
   ```

### 2. Set Up Webhook for Local Testing

1. **Install Stripe CLI** (if not already installed):
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. **Login to Stripe CLI**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to your local server**:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payment/webhook
   ```

4. **Copy the webhook signing secret** (starts with `whsec_`) and add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx
   ```

### 3. Test the Integration

1. **Start your backend server**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Test checkout session creation**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/payment/create-checkout-session \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "tier": "premium",
       "trial_days": 7
     }'
   ```

3. **Monitor webhook events** in the Stripe CLI terminal

### 4. For Production

When ready for production:

1. **Switch to live mode** in Stripe Dashboard
2. **Get live API keys**:
   - Secret key: `sk_live_...`
   - Publishable key: `pk_live_...`
3. **Set up webhook endpoint** in Stripe Dashboard:
   - URL: `https://your-domain.com/api/v1/payment/webhook`
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
4. **Copy production webhook secret** and update `.env`

## Security Notes

- ✅ `.env` is already in `.gitignore` - your keys won't be committed
- ⚠️ Never commit Stripe keys to git
- ⚠️ Use test keys for development, live keys only in production
- ⚠️ Keep webhook secrets secure - they verify webhook authenticity

## Available Endpoints

Once configured, these endpoints will be available:

- `POST /api/v1/payment/create-checkout-session` - Create checkout session
- `POST /api/v1/payment/webhook` - Stripe webhook handler
- `GET /api/v1/payment/verify-subscription/{session_id}` - Verify subscription
- `GET /api/v1/users/me/subscription` - Get user subscription info
- `POST /api/v1/users/me/subscription/cancel` - Cancel subscription

## Troubleshooting

**"Stripe is not configured" error:**
- Make sure `STRIPE_SECRET_KEY` is set in `.env`
- Restart your server after adding keys

**Webhook signature verification fails:**
- Make sure `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe CLI
- For production, use the webhook secret from Stripe Dashboard

**"No Stripe price ID configured" error:**
- Create products in Stripe Dashboard first
- Copy the Price IDs and add them to `.env`

