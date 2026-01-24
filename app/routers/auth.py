"""
Authentication Router
Handles user registration, login, and authentication
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.password import verify_password
from app.utils.jwt import create_access_token, decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Request/Response Models
class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    username: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "username": "johndoe"
            }
        }


class UserRegisterResponse(BaseModel):
    """User registration response"""
    id: str
    email: str
    username: Optional[str]
    subscription_status: str
    trial_ended_at: Optional[str]
    message: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User info response"""
    id: str
    email: str
    username: Optional[str]
    subscription_status: str
    trial_ended_at: Optional[str]
    days_remaining_in_trial: int
    has_active_access: bool


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account with:
    - 7-day trial automatically started
    - Hashed password storage
    - Unique email validation
    """
    try:
        # Validate password strength (basic check)
        if len(request.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Create user
        user = await UserRepository.create_user(
            db=db,
            email=request.email,
            password=request.password,
            username=request.username
        )
        
        return UserRegisterResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            subscription_status=user.subscription_status,
            trial_ended_at=user.trial_ended_at.isoformat() if user.trial_ended_at else None,
            message="User registered successfully. 7-day trial started."
        )
    
    except ValueError as e:
        # Email already exists
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and return JWT access token
    
    Uses OAuth2PasswordRequestForm which expects:
    - username: email address (OAuth2 spec uses 'username' field)
    - password: plain text password
    """
    # Get user by email (OAuth2 uses 'username' field for email)
    user = await UserRepository.get_user_by_email(db, form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await UserRepository.update_user(db, user)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # Subject (user ID)
            "email": user.email,
            "tv": user.token_version  # Token version for revocation
        }
    )
    
    return TokenResponse(access_token=access_token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    This is a dependency that can be used in route handlers to require authentication.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        token_version: int = payload.get("tv", 0)
        
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = await UserRepository.get_user_by_id(db, UUID(user_id))
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Validate token version (for revocation)
        db_token_version = user.token_version or 1
        if token_version < db_token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns user details including subscription status and trial info.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        subscription_status=current_user.subscription_status,
        trial_ended_at=current_user.trial_ended_at.isoformat() if current_user.trial_ended_at else None,
        days_remaining_in_trial=current_user.days_remaining_in_trial(),
        has_active_access=current_user.has_active_access()
    )
