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
import stripe
import os
import logging
from datetime import datetime, timedelta

from app.config import settings

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
        allowed_tiers = ['free', 'premium', 'pro']
        if v.lower() not in allowed_tiers:
            raise ValueError(f'tier must be one of: {", ".join(allowed_tiers)}')
        return v.lower()
    
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
    # Get from environment variables (recommended for security)
    price_ids = {
        "free": os.getenv("STRIPE_PRICE_ID_FREE"),
        "premium": os.getenv("STRIPE_PRICE_ID_PREMIUM"),
        "pro": os.getenv("STRIPE_PRICE_ID_PRO"),
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
        raise HTTPException(
            status_code=400,
            detail=f"No Stripe price ID configured for tier: {request.tier}. Please configure STRIPE_PRICE_ID_{request.tier.upper()} in your environment."
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
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            
            # Cancel URL - user returns here if they cancel
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/signup?cancelled=true",
            
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


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
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
            # Handle successful checkout
            # TODO: Update user subscription status in database
            logger.info(f"Checkout completed for session: {session['id']}")
            
        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            # Handle subscription creation
            # TODO: Update user subscription status in database
            logger.info(f"Subscription created: {subscription['id']}")
            
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            # Handle subscription update
            # TODO: Update user subscription status in database
            logger.info(f"Subscription updated: {subscription['id']}")
            
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Handle subscription cancellation
            # TODO: Update user subscription status in database (mark as cancelled)
            logger.info(f"Subscription cancelled: {subscription['id']}")
            
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            # Handle successful payment (after trial period)
            # TODO: Update user subscription status, send confirmation email
            logger.info(f"Payment succeeded for invoice: {invoice['id']}")
            
        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            # Handle failed payment
            # TODO: Notify user, update subscription status
            logger.warning(f"Payment failed for invoice: {invoice['id']}")
        
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
):
    """
    Verify subscription status after checkout.
    Frontend calls this after redirect from Stripe.
    
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
