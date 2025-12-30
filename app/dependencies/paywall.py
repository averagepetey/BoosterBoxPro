"""
Paywall Dependencies
Require active subscription or trial for API access
"""
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.subscription_service import SubscriptionService
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


async def require_active_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Require active subscription or trial for API access
    
    This dependency checks if the user has active access (trial or subscription).
    If not, raises 403 Forbidden error.
    
    Args:
        current_user: Authenticated user (from get_current_user)
        db: Database session
        
    Returns:
        User object (guaranteed to have active access)
        
    Raises:
        HTTPException: 403 if user does not have active access
    """
    if not current_user.has_active_access():
        # Provide helpful error message
        if current_user.subscription_status.value == "trial" and not current_user.is_trial_active():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your trial has expired. Please subscribe to continue accessing the API."
            )
        elif current_user.subscription_status.value == "expired":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your subscription has expired. Please renew to continue accessing the API."
            )
        elif current_user.subscription_status.value == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your subscription has been cancelled. Please reactivate to continue accessing the API."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active subscription or trial required to access this resource."
            )
    
    return current_user

