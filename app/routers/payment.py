"""
Payment Router
Handles Stripe checkout sessions, subscriptions, and webhooks

Security:
- Mass assignment protection on all request models
- Authentication required for user-specific endpoints
- Stripe webhook signature verification
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import stripe
import os
import logging
from uuid import UUID

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.stripe_service import (
    create_customer,
    get_customer,
    get_subscription,
    update_subscription_status,
    StripeServiceError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])
security = HTTPBearer(auto_error=False)  # Don't auto-error, we handle it

# Initialize Stripe (use settings from config)
stripe.api_key = settings.stripe_secret_key or os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutSessionRequest(BaseModel):
    """Request to create a checkout session"""
    email: EmailStr
    tier: str  # 'free', 'premium', or 'pro'
    trial_days: int = 7
    
    class Config:
        extra = "forbid"  # Mass assignment protection - reject unknown fields
    
    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v: str) -> str:
        """Only allow valid tiers"""
        allowed_tiers = ['free', 'premium', 'pro', 'pro+']
        tier_lower = v.lower()
        # Normalize "pro+" variations
        if tier_lower in ['pro+', 'proplus', 'pro_plus']:
            return 'pro+'
        if tier_lower not in allowed_tiers:
            raise ValueError(f'tier must be one of: {", ".join(allowed_tiers)}')
        return tier_lower
    
    @field_validator('trial_days')
    @classmethod
    def validate_trial_days(cls, v: int) -> int:
        """Limit trial days to reasonable range"""
        if v < 0 or v > 30:
            raise ValueError('trial_days must be between 0 and 30')
        return v


class CheckoutSessionResponse(BaseModel):
    """Response with checkout session URL"""
    url: str
    session_id: str


def get_price_id_for_tier(tier: str) -> Optional[str]:
    """
    Get Stripe Price ID for the given tier
    These should be configured in your Stripe dashboard
    """
    # Get from settings (which loads from .env) or fallback to os.getenv
    # Use settings object first, then fallback to direct env var lookup
    price_ids = {
        "free": getattr(settings, 'stripe_price_id_free', None) or os.getenv("STRIPE_PRICE_ID_FREE"),
        "premium": getattr(settings, 'stripe_price_id_premium', None) or os.getenv("STRIPE_PRICE_ID_PREMIUM"),
        "pro": getattr(settings, 'stripe_price_id_pro', None) or os.getenv("STRIPE_PRICE_ID_PRO"),
        "pro+": getattr(settings, 'stripe_price_id_pro_plus', None) or os.getenv("STRIPE_PRICE_ID_PRO_PLUS"),
    }
    
    return price_ids.get(tier)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optionally get the current user from JWT token.
    Returns None if no valid token provided (allows unauthenticated checkout for new users).
    """
    if not credentials:
        return None
    
    try:
        from app.routers.auth import decode_access_token
        payload = decode_access_token(credentials.credentials)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "is_admin": payload.get("is_admin", False),
        }
    except Exception:
        return None


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Create a Stripe Checkout Session for subscription with trial period.
    
    Security: If user is authenticated, uses their email from token.
    If not authenticated (new signup), uses email from request body.
    """
    # Log checkout attempt
    client_ip = getattr(http_request.state, 'client_ip', 'unknown')
    
    # Use authenticated user's email if available (prevents IDOR)
    if current_user and current_user.get("email"):
        checkout_email = current_user["email"]
        logger.info(f"Checkout session for authenticated user {checkout_email[:3]}*** from {client_ip}")
    else:
        # For new signups, allow email from request body
        checkout_email = request.email
        logger.info(f"Checkout session for new signup {checkout_email[:3]}*** from {client_ip}")
    
    if not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe is not configured. Please set STRIPE_SECRET_KEY environment variable."
        )
    
    # Get the price ID for the selected tier
    price_id = get_price_id_for_tier(request.tier)
    
    if not price_id:
        # Normalize tier name for error message
        tier_env_name = request.tier.upper().replace('+', '_PLUS')
        raise HTTPException(
            status_code=400,
            detail=f"No Stripe price ID configured for tier: {request.tier}. Please configure STRIPE_PRICE_ID_{tier_env_name} in your environment."
        )
    
    try:
        # Create Stripe Checkout Session
        # This will collect payment method but not charge until after trial
        checkout_session = stripe.checkout.Session.create(
            customer_email=checkout_email,  # Use validated email
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            
            # Trial period configuration
            subscription_data={
                "trial_period_days": request.trial_days,
                "trial_settings": {
                    "end_behavior": {
                        "missing_payment_method": "cancel",  # Cancel if no payment method after trial
                    }
                }
            },
            
            # Success URL - user returns here after successful checkout
            success_url=f"{os.getenv('FRONTEND_URL', 'https://boosterboxpro.vercel.app')}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            
            # Cancel URL - user returns here if they cancel
            cancel_url=f"{os.getenv('FRONTEND_URL', 'https://boosterboxpro.vercel.app')}/signup?cancelled=true",
            
            # Metadata to track user and tier
            metadata={
                "user_email": checkout_email,
                "tier": request.tier,
                "trial_days": str(request.trial_days),
                "authenticated": str(current_user is not None),
            },
            
            # Allow promotion codes
            allow_promotion_codes=True,
            
            # Collect billing address
            billing_address_collection="required",
        )
        
        return CheckoutSessionResponse(
            url=checkout_session.url,
            session_id=checkout_session.id
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.get("/webhook")
async def stripe_webhook_get():
    """Stripe webhook only accepts POST. GET returns 405."""
    raise HTTPException(status_code=405, detail="Method Not Allowed. Use POST for Stripe webhooks.")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """
    Handle Stripe webhooks for subscription events.
    Configure this URL in Stripe Dashboard: https://your-domain.com/payment/webhook
    
    SECURITY: Verifies Stripe signature to prevent fake webhook attacks.
    Without this, attackers could fake "payment succeeded" events.
    """
    
    if not stripe.api_key:
        logger.error("Stripe webhook called but Stripe not configured")
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    webhook_secret = settings.stripe_webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if not webhook_secret:
        logger.error("Stripe webhook called but STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(
            status_code=500,
            detail="Webhook secret not configured"
        )
    
    if not stripe_signature:
        logger.warning("Stripe webhook called without signature header")
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    # CRITICAL: Read raw body for signature verification
    # Stripe signs the raw bytes, not parsed JSON
    try:
        payload = await request.body()
    except Exception as e:
        logger.error(f"Failed to read webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Failed to read payload")
    
    try:
        # SECURITY: Verify webhook signature
        # This prevents attackers from faking webhook events
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
        
        logger.info(f"Stripe webhook received: {event['type']}")
        
        # Handle different event types
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            customer_email = session.get("customer_email")
            subscription_id = session.get("subscription")
            
            if customer_email:
                # Find user by email
                stmt = select(User).where(User.email == customer_email)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    # Update user with Stripe customer ID if available
                    if session.get("customer"):
                        user.stripe_customer_id = session["customer"]
                    
                    # Update subscription ID if available
                    if subscription_id:
                        user.stripe_subscription_id = subscription_id
                        # Get subscription details to determine status
                        subscription = get_subscription(subscription_id)
                        if subscription:
                            user.subscription_status = update_subscription_status(subscription)
                    
                    await db.commit()
                    logger.info(f"Updated user {user.email} after checkout session {session['id']}")
                else:
                    logger.warning(f"User not found for email {customer_email} in checkout session")
        
        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")
            
            # Find user by Stripe customer ID
            if customer_id:
                stmt = select(User).where(User.stripe_customer_id == customer_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user.stripe_subscription_id = subscription["id"]
                    user.subscription_status = update_subscription_status(subscription)
                    await db.commit()
                    logger.info(f"Updated user {user.email} with new subscription {subscription['id']}")
        
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            
            # Find user by subscription ID
            stmt = select(User).where(User.stripe_subscription_id == subscription_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.subscription_status = update_subscription_status(subscription)
                await db.commit()
                logger.info(f"Updated subscription status for user {user.email}")
        
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            
            # Find user by subscription ID
            stmt = select(User).where(User.stripe_subscription_id == subscription_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.subscription_status = "cancelled"
                # Optionally clear subscription ID
                # user.stripe_subscription_id = None
                await db.commit()
                logger.info(f"Marked subscription as cancelled for user {user.email}")
        
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            
            if subscription_id:
                # Find user by subscription ID
                stmt = select(User).where(User.stripe_subscription_id == subscription_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    # Ensure subscription is marked as active after successful payment
                    user.subscription_status = "active"
                    await db.commit()
                    logger.info(f"Payment succeeded, activated subscription for user {user.email}")
        
        elif event["type"] == "invoice.payment_failed":
                invoice = event["data"]["object"]
                subscription_id = invoice.get("subscription")
                
                if subscription_id:
                    # Find user by subscription ID
                    stmt = select(User).where(User.stripe_subscription_id == subscription_id)
                    result = await db.execute(stmt)
                    user = result.scalar_one_or_none()
                    
                    if user:
                        # Mark subscription as expired if payment fails
                        user.subscription_status = "expired"
                        await db.commit()
                        logger.warning(f"Payment failed, expired subscription for user {user.email}")
        
        return {"status": "success"}
        
    except ValueError as e:
        # Invalid payload
        logger.warning(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature - possible attack attempt
        logger.warning(f"Invalid Stripe webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")


@router.get("/verify-subscription/{session_id}")
async def verify_subscription(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify subscription status after checkout.
    Frontend calls this after redirect from Stripe.
    
    This endpoint also ensures the user's subscription is updated in the database,
    even if the webhook hasn't processed yet.
    
    Note: Session ID is safe to expose as it's a one-time use token
    and only reveals subscription status, not sensitive data.
    """
    # Log verification attempt
    client_ip = getattr(http_request.state, 'client_ip', 'unknown')
    logger.info(f"Subscription verification attempt for session {session_id[:8]}... from {client_ip}")
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid" or session.subscription:
            logger.info(f"Subscription verified for session {session_id[:8]}...")
            
            # Ensure user subscription is updated in database (in case webhook hasn't processed)
            if session.customer_email:
                from app.models.user import User
                from sqlalchemy import select
                
                stmt = select(User).where(User.email == session.customer_email)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    # Update Stripe customer ID if available
                    if session.get("customer") and not user.stripe_customer_id:
                        user.stripe_customer_id = session["customer"]
                    
                    # Update subscription ID and status if available
                    if session.subscription:
                        if not user.stripe_subscription_id:
                            user.stripe_subscription_id = session.subscription
                        
                        # Get subscription details to determine status
                        subscription = get_subscription(session.subscription)
                        if subscription:
                            user.subscription_status = update_subscription_status(subscription)
                            # Ensure trial dates are set if in trial
                            if subscription.status == 'trialing' and subscription.trial_end:
                                from datetime import datetime, timezone
                                if not user.trial_started_at:
                                    user.trial_started_at = datetime.fromtimestamp(subscription.trial_start, tz=timezone.utc)
                                if not user.trial_ended_at:
                                    user.trial_ended_at = datetime.fromtimestamp(subscription.trial_end, tz=timezone.utc)
                        
                        await db.commit()
                        logger.info(f"Updated user {user.email} subscription from verify endpoint")
            
            return {
                "verified": True,
                "subscription_id": session.subscription,
                # Only return masked email for privacy
                "customer_email": f"{session.customer_email[:3]}***" if session.customer_email else None,
            }
        else:
            return {
                "verified": False,
                "message": "Subscription not yet active",
            }
            
    except stripe.error.StripeError as e:
        logger.warning(f"Stripe error during verification: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Unable to verify subscription"  # Don't expose Stripe error details
        )


@router.post("/create-portal-session")
async def create_portal_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe Customer Portal session.

    Allows users to manage their subscription, payment method, and invoices.
    Requires the user to have an existing Stripe customer ID.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    from app.routers.auth import get_current_user as _get_user
    from fastapi import Request as _Req

    # Resolve current user from token
    from app.routers.auth import decode_access_token
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No billing account found. You'll be able to manage billing after subscribing to a paid plan.",
        )

    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    try:
        frontend_url = os.getenv("FRONTEND_URL", "https://boosterboxpro.vercel.app")
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{frontend_url}/account",
        )
        return {"url": portal_session.url}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal session error: {e}")
        raise HTTPException(status_code=500, detail="Unable to create billing portal session")
