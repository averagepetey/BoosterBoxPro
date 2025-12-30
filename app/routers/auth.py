"""
Authentication Router
Handles user registration, login, and authentication
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserResponse,
)
from app.utils.jwt import create_access_token
from app.utils.password import verify_password
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user
    
    Creates a new user account with email and password.
    Automatically starts a 7-day free trial.
    
    Returns:
        User information (no password)
    """
    try:
        # Create user with trial (password hashing handles length limits)
        user = await UserRepository.create(
            db=db,
            email=request.email,
            password=request.password,
            username=request.username,
            start_trial=True,
            trial_days=7
        )
        
        return UserRegisterResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            subscription_status=user.subscription_status.value,
            trial_ended_at=user.trial_ended_at
        )
    
    except ValueError as e:
        # Check if it's an email conflict or password issue
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            # Email already exists
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        else:
            # Password or other validation error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and get JWT access token
    
    Authenticates user with email and password.
    Returns JWT token for subsequent API requests.
    
    Returns:
        JWT access token and user info
    """
    # Get user by email
    user = await UserRepository.get_by_email(db, request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    await UserRepository.update_last_login(db, user.id)
    
    # Create access token
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=token_data)
    
    # Get trial days remaining
    trial_days_remaining = user.days_remaining_in_trial() if user.is_trial_active() else None
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        subscription_status=user.subscription_status.value,
        trial_days_remaining=trial_days_remaining
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information
    
    Returns the current user's profile and subscription status.
    Requires authentication.
    """
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        subscription_status=current_user.subscription_status.value,
        trial_started_at=current_user.trial_started_at,
        trial_ended_at=current_user.trial_ended_at,
        trial_days_remaining=current_user.days_remaining_in_trial(),
        has_active_access=current_user.has_active_access()
    )

