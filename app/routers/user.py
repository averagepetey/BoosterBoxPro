"""
User Router
Handles user profile and subscription management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.subscription_service import get_user_subscription_info
from app.services.stripe_service import cancel_subscription, StripeServiceError

router = APIRouter(prefix="/users", tags=["users"])


class UpdateProfileRequest(BaseModel):
    """Request model for profile updates"""
    discord_handle: Optional[str] = None

    class Config:
        extra = "forbid"


class ProfileResponse(BaseModel):
    """Response model for profile data"""
    id: str
    email: str
    discord_handle: Optional[str]
    subscription_status: str
    created_at: Optional[str]


class SubscriptionInfoResponse(BaseModel):
    """Response model for subscription information"""
    has_access: bool
    subscription_status: str
    trial_active: bool
    days_remaining_in_trial: Optional[int]
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]


class CancelSubscriptionResponse(BaseModel):
    """Response model for subscription cancellation"""
    message: str
    cancelled: bool
    cancel_at_period_end: bool


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns:
        User information including email, role, and subscription status
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "subscription_status": current_user.subscription_status,
        "discord_handle": current_user.discord_handle,
        "trial_started_at": current_user.trial_started_at.isoformat() if current_user.trial_started_at else None,
        "trial_ended_at": current_user.trial_ended_at.isoformat() if current_user.trial_ended_at else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.put("/me/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.

    Currently supports updating discord_handle.
    """
    if profile_data.discord_handle is not None:
        handle = profile_data.discord_handle.strip()
        if len(handle) > 37:
            from fastapi import HTTPException, status as http_status
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Discord handle must be 37 characters or fewer",
            )
        current_user.discord_handle = handle if handle else None

    await db.commit()
    await db.refresh(current_user)

    return ProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        discord_handle=current_user.discord_handle,
        subscription_status=current_user.subscription_status,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )


@router.get("/me/subscription", response_model=SubscriptionInfoResponse)
async def get_user_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's subscription information
    
    Returns:
        Detailed subscription information including trial status and access
    """
    info = await get_user_subscription_info(db, str(current_user.id))
    return SubscriptionInfoResponse(**info)


@router.post("/me/subscription/cancel", response_model=CancelSubscriptionResponse)
async def cancel_user_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cancel_immediately: bool = False
):
    """
    Cancel user's subscription
    
    Args:
        cancel_immediately: If True, cancel immediately. If False, cancel at period end.
    
    Returns:
        Confirmation of cancellation
    """
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found to cancel"
        )
    
    try:
        subscription = cancel_subscription(
            current_user.stripe_subscription_id,
            cancel_immediately=cancel_immediately
        )
        
        # Update user status in database
        current_user.subscription_status = "cancelled"
        await db.commit()
        
        return CancelSubscriptionResponse(
            message="Subscription cancelled successfully" if cancel_immediately else "Subscription will be cancelled at period end",
            cancelled=True,
            cancel_at_period_end=not cancel_immediately
        )
    except StripeServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

