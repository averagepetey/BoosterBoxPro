"""
Subscription Router
Handles subscription management endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.subscription_service import SubscriptionService
from app.services.stripe_service import StripeService
from app.schemas.auth import SubscriptionStatusResponse
from pydantic import BaseModel


router = APIRouter(prefix="/users/me/subscription", tags=["Subscription"])


class CreateSubscriptionRequest(BaseModel):
    """Request schema for creating a subscription"""
    price_id: str = "..."  # Stripe price ID


class CancelSubscriptionResponse(BaseModel):
    """Response schema for cancelling a subscription"""
    message: str
    subscription_status: str


@router.get("", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's subscription status
    
    Returns subscription status, trial info, and access status.
    """
    return SubscriptionStatusResponse(
        subscription_status=current_user.subscription_status.value,
        trial_active=current_user.is_trial_active(),
        trial_days_remaining=current_user.days_remaining_in_trial() if current_user.is_trial_active() else None,
        subscription_active=current_user.is_subscription_active(),
        has_active_access=current_user.has_active_access(),
        stripe_customer_id=current_user.stripe_customer_id,
        stripe_subscription_id=current_user.stripe_subscription_id,
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new subscription for the current user
    
    Creates a Stripe subscription and links it to the user account.
    """
    subscription_service = SubscriptionService(db)
    
    try:
        # Check if user already has an active subscription
        if current_user.is_subscription_active():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )
        
        # Create subscription
        user = await subscription_service.create_stripe_subscription(
            user=current_user,
            price_id=request.price_id,
            trial_days=None  # User already had trial, don't add trial to subscription
        )
        
        return SubscriptionStatusResponse(
            subscription_status=user.subscription_status.value,
            trial_active=user.is_trial_active(),
            trial_days_remaining=user.days_remaining_in_trial() if user.is_trial_active() else None,
            subscription_active=user.is_subscription_active(),
            has_active_access=user.has_active_access(),
            stripe_customer_id=user.stripe_customer_id,
            stripe_subscription_id=user.stripe_subscription_id,
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subscription: {str(e)}"
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel the current user's subscription
    
    Cancels the Stripe subscription and updates user status.
    """
    subscription_service = SubscriptionService(db)
    
    try:
        if not current_user.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have an active subscription"
            )
        
        user = await subscription_service.cancel_subscription(current_user)
        
        return CancelSubscriptionResponse(
            message="Subscription cancelled successfully",
            subscription_status=user.subscription_status.value
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling subscription: {str(e)}"
        )

