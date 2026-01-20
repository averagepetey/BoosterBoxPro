"""
Payment Router
Handles Stripe checkout sessions, subscriptions, and webhooks
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import stripe
import os
from datetime import datetime, timedelta

from app.config import settings

router = APIRouter(prefix="/payment", tags=["payment"])  # Note: This should be /api/v1/payment but keeping as-is for now
security = HTTPBearer()

# Initialize Stripe (use settings from config)
stripe.api_key = settings.stripe_secret_key or os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutSessionRequest(BaseModel):
    email: EmailStr
    tier: str  # 'free', 'premium', or 'pro'
    trial_days: int = 7


class CheckoutSessionResponse(BaseModel):
    url: str
    session_id: str


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify JWT token and extract user ID
    For now, this is a placeholder - should integrate with your auth system
    """
    token = credentials.credentials
    # TODO: Verify token with your auth system and return user ID
    # For now, we'll use the token as a simple check
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    # In a real implementation, decode JWT and extract user_id
    return "user_id_from_token"  # Placeholder


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


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    # user_id: str = Depends(get_current_user_id),  # Uncomment when auth is ready
):
    """
    Create a Stripe Checkout Session for subscription with trial period
    Flow: User signs up → This endpoint → Redirect to Stripe → 7-day trial → Charge after trial
    """
    
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
            customer_email=request.email,
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
                "user_email": request.email,
                "tier": request.tier,
                "trial_days": str(request.trial_days),
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
    payload: str = Header(None),
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """
    Handle Stripe webhooks for subscription events
    Configure this URL in Stripe Dashboard: https://your-domain.com/payment/webhook
    """
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    webhook_secret = settings.stripe_webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="STRIPE_WEBHOOK_SECRET not configured"
        )
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
        
        # Handle different event types
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Handle successful checkout
            # TODO: Update user subscription status in database
            print(f"Checkout completed for session: {session['id']}")
            
        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            # Handle subscription creation
            # TODO: Update user subscription status in database
            print(f"Subscription created: {subscription['id']}")
            
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            # Handle subscription update
            # TODO: Update user subscription status in database
            print(f"Subscription updated: {subscription['id']}")
            
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Handle subscription cancellation
            # TODO: Update user subscription status in database (mark as cancelled)
            print(f"Subscription cancelled: {subscription['id']}")
            
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            # Handle successful payment (after trial period)
            # TODO: Update user subscription status, send confirmation email
            print(f"Payment succeeded for invoice: {invoice['id']}")
            
        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            # Handle failed payment
            # TODO: Notify user, update subscription status
            print(f"Payment failed for invoice: {invoice['id']}")
        
        return {"status": "success"}
        
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")


@router.get("/verify-subscription/{session_id}")
async def verify_subscription(session_id: str):
    """
    Verify subscription status after checkout
    Frontend calls this after redirect from Stripe
    """
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid" or session.subscription:
            return {
                "verified": True,
                "subscription_id": session.subscription,
                "customer_email": session.customer_email,
            }
        else:
            return {
                "verified": False,
                "message": "Subscription not yet active",
            }
            
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )

