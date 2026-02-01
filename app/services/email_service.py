"""
Email Service using Resend
Handles password reset and email verification emails.
"""

import logging
import resend
from app.config import settings

logger = logging.getLogger(__name__)

# Sender address — use onboarding@resend.dev until custom domain is verified in Resend
FROM_ADDRESS = "BoosterBoxPro <onboarding@resend.dev>"


def _get_frontend_url() -> str:
    return settings.frontend_url.rstrip("/")


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send a password reset email. Returns True on success, False on failure.
    Never raises — prevents email enumeration."""
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — skipping password reset email")
        return False

    resend.api_key = settings.resend_api_key
    frontend_url = _get_frontend_url()
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; color: #e0e0e0; background: #0a0a0a;">
      <h2 style="color: #ffffff; margin-bottom: 8px;">Reset Your Password</h2>
      <p style="color: #999; margin-bottom: 24px;">You requested a password reset for your BoosterBoxPro account.</p>
      <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background: #22c55e; color: #000; text-decoration: none; border-radius: 6px; font-weight: 600;">Reset Password</a>
      <p style="color: #666; font-size: 13px; margin-top: 24px;">This link expires in 15 minutes. If you didn't request this, ignore this email.</p>
      <hr style="border: none; border-top: 1px solid #222; margin: 32px 0 16px;" />
      <p style="color: #444; font-size: 12px;">BoosterBoxPro — TCG Market Intelligence</p>
    </div>
    """

    try:
        resend.Emails.send({
            "from": FROM_ADDRESS,
            "to": [to_email],
            "subject": "Reset your BoosterBoxPro password",
            "html": html,
        })
        logger.info(f"Password reset email sent to {to_email[:3]}***")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False


def send_verification_email(to_email: str, verification_token: str) -> bool:
    """Send an email verification email. Returns True on success, False on failure."""
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — skipping verification email")
        return False

    resend.api_key = settings.resend_api_key
    frontend_url = _get_frontend_url()
    verify_link = f"{frontend_url}/verify-email?token={verification_token}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; color: #e0e0e0; background: #0a0a0a;">
      <h2 style="color: #ffffff; margin-bottom: 8px;">Verify Your Email</h2>
      <p style="color: #999; margin-bottom: 24px;">Welcome to BoosterBoxPro! Click below to verify your email address.</p>
      <a href="{verify_link}" style="display: inline-block; padding: 12px 24px; background: #22c55e; color: #000; text-decoration: none; border-radius: 6px; font-weight: 600;">Verify Email</a>
      <p style="color: #666; font-size: 13px; margin-top: 24px;">This link expires in 24 hours.</p>
      <hr style="border: none; border-top: 1px solid #222; margin: 32px 0 16px;" />
      <p style="color: #444; font-size: 12px;">BoosterBoxPro — TCG Market Intelligence</p>
    </div>
    """

    try:
        resend.Emails.send({
            "from": FROM_ADDRESS,
            "to": [to_email],
            "subject": "Verify your BoosterBoxPro email",
            "html": html,
        })
        logger.info(f"Verification email sent to {to_email[:3]}***")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False
