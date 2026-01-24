"""
Paywall Dependency
Requires user to have active access (trial or subscription)

This dependency should be added to all protected endpoints that require
an active subscription or trial period.
"""

from fastapi import HTTPException, Depends, status
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.subscription_service import has_active_access

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except:
    pass


async def require_active_subscription(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires user to have active access (trial or subscription).
    
    This checks:
    - User is authenticated (via get_current_user)
    - User has active trial OR active subscription
    
    Raises:
        HTTPException 403: If user does not have active access
        HTTPException 401: If user is not authenticated (from get_current_user)
    
    Returns:
        User: The authenticated user with active access
    """
    if not has_active_access(current_user):
        if logger:
            logger.warning(f"User {current_user.email} attempted to access protected resource without active subscription")
        
        # Check if trial expired
        from datetime import datetime
        trial_expired = (
            current_user.trial_ended_at and 
            current_user.trial_ended_at <= datetime.utcnow()
        )
        
        if trial_expired:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your trial period has expired. Please subscribe to continue accessing premium features."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active subscription or trial required to access this resource."
            )
    
    return current_user

