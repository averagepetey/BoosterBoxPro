"""
Subscription Service
Handles subscription logic and trial management
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, SubscriptionStatus
from app.repositories.user_repository import UserRepository
from app.services.stripe_service import StripeService


class SubscriptionService:
    """Service for subscription and trial management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stripe_service = StripeService()
    
    @staticmethod
    def check_trial_status(user: User) -> bool:
        """
        Check if user's trial is currently active
        
        Args:
            user: User object
            
        Returns:
            True if trial is active, False otherwise
        """
        return user.is_trial_active()
    
    @staticmethod
    def has_active_access(user: User) -> bool:
        """
        Check if user has active access (trial or subscription)
        
        Args:
            user: User object
            
        Returns:
            True if user has active access, False otherwise
        """
        return user.has_active_access()
    
    async def start_trial(self, user: User, days: int = 7) -> User:
        """
        Start a trial period for a user
        
        Args:
            user: User object
            days: Number of days for trial (default: 7)
            
        Returns:
            Updated User object
        """
        user.start_trial(days=days)
        return await UserRepository.update(self.db, user)
    
    async def create_stripe_subscription(
        self,
        user: User,
        price_id: str,
        trial_days: Optional[int] = None
    ) -> User:
        """
        Create a Stripe subscription for a user
        
        Args:
            user: User object
            price_id: Stripe price ID
            trial_days: Optional trial period in days (if user hasn't used trial)
            
        Returns:
            Updated User object with Stripe subscription info
        """
        # Get or create Stripe customer
        if not user.stripe_customer_id:
            stripe_customer = self.stripe_service.create_customer(
                email=user.email,
                name=user.username
            )
            user.stripe_customer_id = stripe_customer.id
        
        # Create subscription
        # Only include trial if user hasn't used trial yet
        trial_period = None
        if trial_days and not user.trial_started_at:
            trial_period = trial_days
        
        stripe_subscription = self.stripe_service.create_subscription(
            customer_id=user.stripe_customer_id,
            price_id=price_id,
            trial_days=trial_period
        )
        
        # Update user with subscription info
        user.stripe_subscription_id = stripe_subscription.id
        user.subscription_status = SubscriptionStatus.ACTIVE
        
        return await UserRepository.update(self.db, user)
    
    async def cancel_subscription(self, user: User) -> User:
        """
        Cancel a user's Stripe subscription
        
        Args:
            user: User object
            
        Returns:
            Updated User object
        """
        if not user.stripe_subscription_id:
            raise ValueError("User does not have an active subscription")
        
        # Cancel subscription in Stripe
        self.stripe_service.cancel_subscription(user.stripe_subscription_id)
        
        # Update user status
        user.subscription_status = SubscriptionStatus.CANCELLED
        user.stripe_subscription_id = None
        
        return await UserRepository.update(self.db, user)
    
    async def update_subscription_from_webhook(
        self,
        stripe_subscription_id: str,
        status: str
    ) -> Optional[User]:
        """
        Update user subscription status from Stripe webhook event
        
        Args:
            stripe_subscription_id: Stripe subscription ID
            status: Subscription status from Stripe
            
        Returns:
            Updated User object or None if not found
        """
        # Find user by subscription ID
        # Note: This assumes we store subscription_id - if not, we'd need to query differently
        users = await self.db.execute(
            select(User).where(User.stripe_subscription_id == stripe_subscription_id)
        )
        user = users.scalar_one_or_none()
        
        if not user:
            return None
        
        # Map Stripe status to our status
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "canceled": SubscriptionStatus.CANCELLED,
            "past_due": SubscriptionStatus.EXPIRED,
            "unpaid": SubscriptionStatus.EXPIRED,
        }
        
        our_status = status_map.get(status, SubscriptionStatus.EXPIRED)
        user.subscription_status = our_status
        
        return await UserRepository.update(self.db, user)

