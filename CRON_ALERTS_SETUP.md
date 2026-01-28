# Cron Job Alerts Setup

> **Purpose:** Get notified when the daily refresh cron job fails  
> **Time:** 10-15 minutes

---

## Option 1: Render Notifications (Easiest)

**Render has built-in notifications for failed cron jobs.**

1. **Render Dashboard** → your project → **boosterboxpro-daily-refresh** cron job
2. Go to **Settings** → **Notifications** (or **Alerts**)
3. Enable **Email notifications** for:
   - Cron job failures
   - Cron job timeouts
4. Add your email address

**That's it!** Render will email you when the cron fails.

---

## Option 2: Email Alerts (SMTP)

**Set up email alerts via SMTP (Gmail, SendGrid, etc.)**

### 1. Get SMTP credentials

**Gmail:**
- Enable "Less secure app access" or use an App Password
- SMTP Host: `smtp.gmail.com`
- SMTP Port: `587`
- Username: your Gmail address
- Password: App Password (generate in Google Account settings)

**SendGrid (recommended for production):**
- Sign up at sendgrid.com
- Create API key
- SMTP Host: `smtp.sendgrid.net`
- SMTP Port: `587`
- Username: `apikey`
- Password: your SendGrid API key

### 2. Set environment variables in Render

**Render → API → Environment** (or Cron Job → Environment):

```
ALERT_EMAIL_TO=your-email@example.com
ALERT_EMAIL_FROM=alerts@boosterboxpro.com  # Optional, defaults to ALERT_EMAIL_TO
ALERT_SMTP_HOST=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_SMTP_USER=your-email@gmail.com
ALERT_SMTP_PASSWORD=your-app-password
```

### 3. Test

Trigger a test failure or wait for the next cron run. You'll get an email if it fails.

---

## Option 3: Slack Alerts

**Get alerts in a Slack channel**

### 1. Create Slack webhook

1. Go to https://api.slack.com/apps
2. Create new app or use existing
3. Go to **Incoming Webhooks** → **Activate Incoming Webhooks**
4. **Add New Webhook to Workspace**
5. Choose a channel (e.g., `#alerts` or `#boosterboxpro`)
6. Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

### 2. Set environment variable in Render

**Render → API → Environment** (or Cron Job → Environment):

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Test

The cron will post to Slack when it fails.

---

## Option 4: Health Check Endpoint (UptimeRobot)

**Monitor cron status via HTTP endpoint**

### 1. Add monitor in UptimeRobot

1. Go to [UptimeRobot Dashboard](https://uptimerobot.com/dashboard)
2. **Add New Monitor**
3. **Monitor Type:** HTTP(s)
4. **URL:** `https://boosterboxpro.onrender.com/health/cron`
5. **Monitoring Interval:** 1 hour (or 5 minutes for more frequent checks)
6. **Alert Contacts:** Add your email/SMS

### 2. How it works

The `/health/cron` endpoint returns:
- `"status": "healthy"` if last run succeeded and was recent (< 25 hours ago)
- `"status": "unhealthy"` if last run failed or hasn't run in > 25 hours

UptimeRobot will alert you when the endpoint returns "unhealthy".

---

## Option 5: Success Alerts (Optional)

**Get notified when cron succeeds (daily confirmation)**

Set in Render → Environment:

```
ALERT_ON_SUCCESS=true
```

This sends a success notification after each successful run. Useful for daily confirmation that everything is working.

---

## Recommended Setup

**For production, use multiple methods:**

1. **Render notifications** (easiest, built-in)
2. **UptimeRobot** monitoring `/health/cron` (redundant check, catches issues even if Render alerts fail)
3. **Email or Slack** (optional, for detailed error messages)

---

## Testing

**To test alerts:**

1. Temporarily break the cron (e.g., set wrong `APIFY_API_TOKEN`)
2. Trigger a run manually
3. Wait for alert (email/Slack/UptimeRobot)
4. Fix the issue
5. Verify next run succeeds

---

## Troubleshooting

**No alerts received:**
- Check environment variables are set correctly in Render
- Check Render logs for "Failed to send alert" warnings
- Verify SMTP credentials (for email) or webhook URL (for Slack)
- Check spam folder (for email)

**Alerts too frequent:**
- Adjust UptimeRobot monitoring interval
- Set `ALERT_ON_SUCCESS=false` to disable success notifications

---

**Ref:** `app/services/alert_service.py`, `scripts/daily_refresh.py`, `main.py` → `/health/cron`
