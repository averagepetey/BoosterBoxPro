"""
Stripe Service
Handles Stripe customer and subscription operations

Security:
- All Stripe API calls are server-side only
- Customer IDs are stored in database, not exposed to frontend
- Webhook signature verification prevents fake events
"""

import stripe
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class StripeServiceError(Exception):
    """Custom exception for Stripe service errors"""
    pass


def create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
    """
    Create a Stripe customer
    
    Args:
        email: Customer email address
        name: Optional customer name
    
    Returns:
        stripe.Customer object
    
    Raises:
        StripeServiceError: If Stripe API call fails
    """
    if not stripe.api_key:
        raise StripeServiceError("Stripe is not configured. Set STRIPE_SECRET_KEY environment variable.")
    
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "source": "boosterboxpro",
            }
        )
        logger.info(f"Created Stripe customer {customer.id} for {email[:3]}***")
        return customer
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating customer: {e}")
        raise StripeServiceError(f"Failed to create customer: {str(e)}")


def get_customer(customer_id: str) -> Optional[stripe.Customer]:
    """
    Retrieve a Stripe customer by ID
    
    Args:
        customer_id: Stripe customer ID
    
    Returns:
        stripe.Customer object or None if not found
    
    Raises:
        StripeServiceError: If Stripe API call fails
    """
    if not stripe.api_key:
        raise StripeServiceError("Stripe is not configured")
    
    try:
        customer = stripe.Customer.retrieve(customer_id)
        return customer
    except stripe.error.InvalidRequestError:
        # Customer doesn't exist
        return None
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving customer: {e}")
        raise StripeServiceError(f"Failed to retrieve customer: {str(e)}")


def create_subscription(
    customer_id: str,
    price_id: str,
    trial_period_days: int = 0
) -> stripe.Subscription:
    """
    Create a Stripe subscription for a customer
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID for the subscription tier
        trial_period_days: Number of days for trial period (0 = no trial)
    
    Returns:
        stripe.Subscription object
    
    Raises:
        StripeServiceError: If Stripe API call fails
    """
    if not stripe.api_key:
        raise StripeServiceError("Stripe is not configured")
    
    try:
        subscription_params = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }
        
        # Add trial period if specified
        if trial_period_days > 0:
            subscription_params["trial_period_days"] = trial_period_days
            subscription_params["trial_settings"] = {
                "end_behavior": {
                    "missing_payment_method": "cancel"
                }
            }
        
        subscription = stripe.Subscription.create(**subscription_params)
        logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
        return subscription
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {e}")
        raise StripeServiceError(f"Failed to create subscription: {str(e)}")


def get_subscription(subscription_id: str) -> Optional[stripe.Subscription]:
    """
    Retrieve a Stripe subscription by ID
    
    Args:
        subscription_id: Stripe subscription ID
    
    Returns:
        stripe.Subscription object or None if not found
    
    Raises:
        StripeServiceError: If Stripe API call fails
    """
    if not stripe.api_key:
        raise StripeServiceError("Stripe is not configured")
    
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except stripe.error.InvalidRequestError:
        # Subscription doesn't exist
        return None
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving subscription: {e}")
        raise StripeServiceError(f"Failed to retrieve subscription: {str(e)}")


def cancel_subscription(
    subscription_id: str,
    cancel_immediately: bool = False
) -> stripe.Subscription:
    """
    Cancel a Stripe subscription
    
    Args:
        subscription_id: Stripe subscription ID
        cancel_immediately: If True, cancel immediately. If False, cancel at period end.
    
    Returns:
        Updated stripe.Subscription object
    
    Raises:
        StripeServiceError: If Stripe API call fails
    """
    if not stripe.api_key:
        raise StripeServiceError("Stripe is not configured")
    
    try:
        if cancel_immediately:
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"Immediately cancelled subscription {subscription_id}")
        else:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            logger.info(f"Scheduled cancellation for subscription {subscription_id} at period end")
        
        return subscription
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling subscription: {e}")
        raise StripeServiceError(f"Failed to cancel subscription: {str(e)}")


def update_subscription_status(subscription: stripe.Subscription) -> str:
    """
    Determine subscription status from Stripe subscription object
    
    Args:
        subscription: stripe.Subscription object
    
    Returns:
        Status string: 'active', 'trialing', 'past_due', 'canceled', 'unpaid'
    """
    if subscription.status == 'active':
        return 'active'
    elif subscription.status == 'trialing':
        return 'trial'
    elif subscription.status in ['canceled', 'unpaid', 'past_due']:
        return 'expired'
    else:
        return 'expired'

