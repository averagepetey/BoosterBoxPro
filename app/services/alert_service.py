"""
Alert Service
Sends notifications when cron jobs fail or other critical events occur.

Supports:
- Email (SMTP)
- Slack webhook
- Future: SMS, Discord, etc.
"""

import os
import logging
import json
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def send_email_alert(
    subject: str,
    body: str,
    to_email: Optional[str] = None
) -> bool:
    """
    Send email alert via SMTP.
    
    Requires env vars:
    - ALERT_EMAIL_TO: recipient email
    - ALERT_EMAIL_FROM: sender email (optional, defaults to ALERT_EMAIL_TO)
    - ALERT_SMTP_HOST: SMTP server (e.g., smtp.gmail.com)
    - ALERT_SMTP_PORT: SMTP port (default: 587)
    - ALERT_SMTP_USER: SMTP username
    - ALERT_SMTP_PASSWORD: SMTP password
    """
    to_email = to_email or os.getenv("ALERT_EMAIL_TO")
    if not to_email:
        logger.warning("ALERT_EMAIL_TO not set, skipping email alert")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_host = os.getenv("ALERT_SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("ALERT_SMTP_PORT", "587"))
        smtp_user = os.getenv("ALERT_SMTP_USER")
        smtp_password = os.getenv("ALERT_SMTP_PASSWORD")
        from_email = os.getenv("ALERT_EMAIL_FROM", to_email)
        
        if not smtp_user or not smtp_password:
            logger.warning("ALERT_SMTP_USER or ALERT_SMTP_PASSWORD not set, skipping email alert")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email alert sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")
        return False


def send_slack_alert(
    message: str,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send alert to Slack via webhook.
    
    Requires env var:
    - SLACK_WEBHOOK_URL: Slack incoming webhook URL
    """
    webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set, skipping Slack alert")
        return False
    
    try:
        import requests
        
        payload = {
            "text": message,
            "username": "BoosterBoxPro Alerts",
            "icon_emoji": ":warning:"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("Slack alert sent")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False


def alert_cron_failure(
    job_name: str,
    error_message: str,
    phase: Optional[str] = None
) -> None:
    """
    Send alert when a cron job fails.
    
    Args:
        job_name: Name of the cron job (e.g., "daily-refresh")
        error_message: Error message or exception
        phase: Optional phase that failed (e.g., "Apify", "Scraper")
    """
    subject = f"🚨 BoosterBoxPro Cron Job Failed: {job_name}"
    if phase:
        subject += f" ({phase} phase)"
    
    body = f"""
BoosterBoxPro Cron Job Failure Alert

Job: {job_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Phase: {phase or 'Unknown'}

Error:
{error_message}

Please check the logs in Render dashboard for more details.
"""
    
    slack_message = f"🚨 *BoosterBoxPro Cron Job Failed*\n\n*Job:* {job_name}\n*Phase:* {phase or 'Unknown'}\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n*Error:* {error_message}"
    
    # Try both email and Slack
    email_sent = send_email_alert(subject, body)
    slack_sent = send_slack_alert(slack_message)
    
    if not email_sent and not slack_sent:
        logger.warning("No alert channels configured (ALERT_EMAIL_TO or SLACK_WEBHOOK_URL)")


def alert_cron_success(
    job_name: str,
    duration_seconds: float,
    summary: Optional[str] = None
) -> None:
    """
    Optional: Send success notification (useful for daily confirmation).
    
    Args:
        job_name: Name of the cron job
        duration_seconds: How long it took
        summary: Optional summary message
    """
    # Only send success alerts if explicitly enabled
    if os.getenv("ALERT_ON_SUCCESS", "false").lower() != "true":
        return
    
    subject = f"✅ BoosterBoxPro Cron Job Succeeded: {job_name}"
    body = f"""
BoosterBoxPro Cron Job Success

Job: {job_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Duration: {duration_seconds:.1f} seconds ({duration_seconds/60:.1f} minutes)

{summary or 'Job completed successfully.'}
"""
    
    slack_message = f"✅ *BoosterBoxPro Cron Job Succeeded*\n\n*Job:* {job_name}\n*Duration:* {duration_seconds/60:.1f} minutes\n{summary or ''}"
    
    send_email_alert(subject, body)
    send_slack_alert(slack_message)
