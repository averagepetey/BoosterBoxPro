"""
Subscription Service
Handles subscription and trial access checking

This service provides business logic for determining if a user has active access
to the platform (either through trial or paid subscription).
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User

logger = logging.getLogger(__name__)


def check_trial_status(user: User) -> bool:
    """
    Check if user is currently in their trial period
    
    Args:
        user: User model instance
    
    Returns:
        True if user is in trial period, False otherwise
    """
    if not user.trial_ended_at:
        return False
    
    now = datetime.utcnow()
    return user.trial_ended_at > now


def has_active_access(user: User) -> bool:
    """
    Check if user has active access to the platform.
    
    User has access if:
    - They are in trial period (trial_ended_at is in the future), OR
    - They have an active subscription (subscription_status == 'active'), OR
    - They have a trial subscription from Stripe (subscription_status == 'trial')
    
    Args:
        user: User model instance
    
    Returns:
        True if user has active access, False otherwise
    """
    # Pioneer users have full access
    if user.subscription_status == 'pioneer':
        return True

    # Check if trial is still active (based on trial_ended_at date)
    if check_trial_status(user):
        return True

    # Check if subscription is active (paid subscription)
    if user.subscription_status == 'active':
        return True

    # Check if subscription is in trial (Stripe trialing status)
    if user.subscription_status == 'trial':
        return True

    return False


async def get_user_subscription_info(
    db: AsyncSession,
    user_id: str
) -> dict:
    """
    Get comprehensive subscription information for a user
    
    Args:
        db: Database session
        user_id: User UUID as string
    
    Returns:
        Dictionary with subscription information:
        {
            'has_access': bool,
            'subscription_status': str,
            'trial_active': bool,
            'days_remaining_in_trial': Optional[int],
            'stripe_customer_id': Optional[str],
            'stripe_subscription_id': Optional[str],
        }
    """
    from uuid import UUID
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return {
            'has_access': False,
            'subscription_status': 'unknown',
            'trial_active': False,
            'days_remaining_in_trial': None,
            'stripe_customer_id': None,
            'stripe_subscription_id': None,
        }
    
    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return {
            'has_access': False,
            'subscription_status': 'unknown',
            'trial_active': False,
            'days_remaining_in_trial': None,
            'stripe_customer_id': None,
            'stripe_subscription_id': None,
        }
    
    trial_active = check_trial_status(user)
    days_remaining = user.days_remaining_in_trial() if trial_active else None
    
    return {
        'has_access': has_active_access(user),
        'subscription_status': user.subscription_status,
        'trial_active': trial_active,
        'days_remaining_in_trial': days_remaining,
        'stripe_customer_id': user.stripe_customer_id,
        'stripe_subscription_id': user.stripe_subscription_id,
    }


def days_remaining_in_trial(user: User) -> Optional[int]:
    """
    Calculate days remaining in trial period
    
    Args:
        user: User model instance
    
    Returns:
        Number of days remaining, or None if trial has ended or doesn't exist
    """
    return user.days_remaining_in_trial()


def is_subscription_active(user: User) -> bool:
    """
    Check if user has an active paid subscription (not trial)
    
    Args:
        user: User model instance
    
    Returns:
        True if subscription is active, False otherwise
    """
    return user.is_subscription_active()


