# Stripe Integration Testing Guide

## Prerequisites

Before testing, ensure:

1. ✅ **Backend server is running:**
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. ✅ **Stripe CLI is forwarding webhooks:**
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payment/webhook
   ```
   (Keep this terminal open)

3. ✅ **Stripe keys are configured in `.env`:**
   - `STRIPE_SECRET_KEY=sk_test_...`
   - `STRIPE_PUBLISHABLE_KEY=pk_test_...`
   - `STRIPE_WEBHOOK_SECRET=whsec_...` (from Stripe CLI)

4. ✅ **Price ID is configured:**
   - `STRIPE_PRICE_ID_PRO_PLUS=price_...`

---

## Test 1: Quick Health Check

```bash
python test_stripe_integration.py
```

This will:
- ✅ Check if backend is running
- ✅ Test checkout session creation
- ✅ Return checkout URL for testing

**Expected Output:**
```
✅ Backend is running
✅ Checkout session created successfully!
   Session ID: cs_test_...
   Checkout URL: https://checkout.stripe.com/...
```

---

## Test 2: Manual API Test

### Create Checkout Session

```bash
curl -X POST http://localhost:8000/api/v1/payment/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "tier": "pro+",
    "trial_days": 7
  }'
```

**Expected Response:**
```json
{
  "url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "session_id": "cs_test_..."
}
```

### Test with Authenticated User

First, register/login to get a token:
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

Then create checkout with token:
```bash
curl -X POST http://localhost:8000/api/v1/payment/create-checkout-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "email": "test@example.com",
    "tier": "pro+",
    "trial_days": 7
  }'
```

---

## Test 3: Complete Checkout Flow

1. **Open the checkout URL** from Test 1 or 2 in your browser

2. **Use Stripe test card:**
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/34`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)

3. **Complete the checkout**

4. **Watch for webhook events** in your Stripe CLI terminal:
   ```
   --> checkout.session.completed [200]
   --> customer.subscription.created [200]
   --> invoice.payment_succeeded [200]
   ```

5. **Check backend logs** for:
   ```
   ✅ Updated user test@example.com after checkout session
   ✅ Subscription created: sub_...
   ✅ Payment succeeded, activated subscription
   ```

---

## Test 4: Verify Database

Check if user subscription was updated:

```bash
python check_user.py test@example.com
```

**Expected Output:**
```
✅ User found: test@example.com
   ...
   📦 Subscription Info:
   Status: active
   Stripe Customer ID: cus_...
   Stripe Subscription ID: sub_...
   Trial Started: 2026-01-24 ...
   Trial Ends: 2026-01-31 ...
   Days Remaining: 7
```

---

## Test 5: Test Subscription Endpoints

### Get User Subscription Info

```bash
curl -X GET http://localhost:8000/api/v1/users/me/subscription \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "has_access": true,
  "subscription_status": "active",
  "trial_active": true,
  "days_remaining_in_trial": 7,
  "stripe_customer_id": "cus_...",
  "stripe_subscription_id": "sub_..."
}
```

### Cancel Subscription

```bash
curl -X POST http://localhost:8000/api/v1/users/me/subscription/cancel \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"cancel_immediately": false}'
```

**Expected Response:**
```json
{
  "message": "Subscription will be cancelled at period end",
  "cancelled": true,
  "cancel_at_period_end": true
}
```

---

## Test 6: Test Webhook Events

### Trigger Test Events (Stripe CLI)

```bash
# Test checkout completion
stripe trigger checkout.session.completed

# Test subscription creation
stripe trigger customer.subscription.created

# Test payment success
stripe trigger invoice.payment_succeeded

# Test payment failure
stripe trigger invoice.payment_failed
```

Watch your backend logs and Stripe CLI terminal for events.

---

## Test 7: Test Paywall Protection

Try accessing a protected endpoint without subscription:

```bash
# This should fail if user doesn't have active subscription
curl -X GET http://localhost:8000/api/v1/users/me/subscription \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response (if no subscription):**
```json
{
  "detail": "Active subscription or trial required to access this resource."
}
```

---

## Troubleshooting

### "Stripe is not configured"
- ✅ Check `STRIPE_SECRET_KEY` is set in `.env`
- ✅ Restart backend server after adding keys

### "No Stripe price ID configured"
- ✅ Check `STRIPE_PRICE_ID_PRO_PLUS` is set in `.env`
- ✅ Verify the tier name matches ("pro+")

### Webhook events not received
- ✅ Check Stripe CLI is running: `stripe listen --forward-to localhost:8000/api/v1/payment/webhook`
- ✅ Verify `STRIPE_WEBHOOK_SECRET` matches the CLI secret
- ✅ Check backend logs for webhook errors

### User subscription not updated
- ✅ Check webhook events were received
- ✅ Verify webhook handler is updating database
- ✅ Check backend logs for errors
- ✅ Verify user email matches in Stripe and database

### "Invalid signature" error
- ✅ Make sure `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe CLI
- ✅ For production, use the webhook secret from Stripe Dashboard

---

## Test Cards

Stripe provides test cards for different scenarios:

| Card Number | Scenario |
|------------|----------|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0025 0000 3155` | Requires authentication |

More test cards: https://stripe.com/docs/testing

---

## Success Criteria

✅ **Integration is working if:**
1. Checkout session is created successfully
2. User can complete checkout with test card
3. Webhook events are received and processed
4. User subscription is updated in database
5. Subscription endpoints return correct data
6. Paywall blocks access without subscription

---

## Next Steps

After successful testing:
1. ✅ Test with different tiers (if you have Premium plan)
2. ✅ Test subscription cancellation
3. ✅ Test payment failure scenarios
4. ✅ Test trial expiration
5. ✅ Prepare for production (switch to live keys)

---

**Happy Testing! 🎉**


