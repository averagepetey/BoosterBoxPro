# Install Stripe CLI

The Stripe CLI is needed to forward webhook events to your local development server.

## Installation Options

### Option 1: Homebrew (Recommended for macOS)

```bash
brew install stripe/stripe-cli/stripe
```

If you get permission errors:
```bash
sudo chown -R $(whoami) /opt/homebrew/Cellar
brew install stripe/stripe-cli/stripe
```

### Option 2: Direct Download

1. Visit: https://github.com/stripe/stripe-cli/releases/latest
2. Download the macOS binary:
   - For Intel Macs: `stripe_X.X.X_macOS_x86_64.tar.gz`
   - For Apple Silicon: `stripe_X.X.X_macOS_arm64.tar.gz`
3. Extract and install:
   ```bash
   tar -xzf stripe_X.X.X_macOS_x86_64.tar.gz
   sudo mv stripe /usr/local/bin/
   ```

### Option 3: Using npm (if you have Node.js)

```bash
npm install -g stripe-cli
```

## Verify Installation

After installation, verify it works:

```bash
stripe --version
```

You should see something like: `stripe version X.X.X`

## Setup Webhook Forwarding

1. **Login to Stripe** (first time only):
   ```bash
   stripe login
   ```
   This will open your browser to authenticate.

2. **Start webhook forwarding** (run this in a separate terminal):
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payment/webhook
   ```

3. **Copy the webhook signing secret**:
   When you run the command above, Stripe will output something like:
   ```
   > Ready! Your webhook signing secret is whsec_xxxxx (^C to quit)
   ```

4. **Add to your `.env` file**:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx
   ```

5. **Keep the terminal running** - this forwards webhooks to your local server.

## Testing

Once set up, you can test webhook events:

```bash
# Trigger a test event
stripe trigger payment_intent.succeeded
```

You should see the event appear in your webhook forwarding terminal and your backend logs.

## Troubleshooting

**"command not found: stripe"**
- Make sure the installation completed successfully
- Try restarting your terminal
- Check if `/usr/local/bin` is in your PATH: `echo $PATH`

**"Permission denied"**
- For Homebrew: `sudo chown -R $(whoami) /opt/homebrew/Cellar`
- For direct install: Make sure you have sudo permissions

**Webhook not receiving events**
- Make sure the forwarding command is still running
- Check that your backend is running on port 8000
- Verify the webhook URL is correct: `localhost:8000/api/v1/payment/webhook`

## Alternative: Skip Webhook Testing (Not Recommended)

If you can't install Stripe CLI right now, you can:
1. Skip webhook testing for now
2. Test the checkout flow manually
3. Set up webhooks later when deploying to production

However, webhook testing is highly recommended to ensure your integration works correctly.

