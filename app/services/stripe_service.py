"""
Stripe Service
Handles Stripe API integration for payments and subscriptions
"""
from typing import Optional
import stripe
from app.config import settings

# Initialize Stripe with secret key from config
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for Stripe API operations"""
    
    @staticmethod
    def create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email address
            name: Optional customer name
            
        Returns:
            Stripe Customer object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        customer_data = {
            "email": email,
        }
        
        if name:
            customer_data["name"] = name
        
        return stripe.Customer.create(**customer_data)
    
    @staticmethod
    def get_customer(customer_id: str) -> stripe.Customer:
        """
        Get a Stripe customer by ID
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            Stripe Customer object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        return stripe.Customer.retrieve(customer_id)
    
    @staticmethod
    def create_subscription(
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None
    ) -> stripe.Subscription:
        """
        Create a Stripe subscription
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the subscription
            trial_days: Optional trial period in days
            
        Returns:
            Stripe Subscription object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        subscription_data = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }
        
        if trial_days:
            subscription_data["trial_period_days"] = trial_days
        
        return stripe.Subscription.create(**subscription_data)
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> stripe.Subscription:
        """
        Cancel a Stripe subscription
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Cancelled Stripe Subscription object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        return stripe.Subscription.delete(subscription_id)
    
    @staticmethod
    def get_subscription(subscription_id: str) -> stripe.Subscription:
        """
        Get a Stripe subscription by ID
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Stripe Subscription object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        return stripe.Subscription.retrieve(subscription_id)
    
    @staticmethod
    def create_payment_intent(
        customer_id: str,
        amount: int,  # Amount in cents
        currency: str = "usd",
        metadata: Optional[dict] = None
    ) -> stripe.PaymentIntent:
        """
        Create a Stripe PaymentIntent
        
        Args:
            customer_id: Stripe customer ID
            amount: Amount in cents
            currency: Currency code (default: "usd")
            metadata: Optional metadata dictionary
            
        Returns:
            Stripe PaymentIntent object
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        if not settings.stripe_secret_key:
            raise ValueError("Stripe secret key not configured")
        
        intent_data = {
            "customer": customer_id,
            "amount": amount,
            "currency": currency,
        }
        
        if metadata:
            intent_data["metadata"] = metadata
        
        return stripe.PaymentIntent.create(**intent_data)

