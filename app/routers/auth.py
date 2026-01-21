"""
Authentication Router
Handles user registration, login, and authentication

Security Features:
- Rate limiting on auth endpoints
- Password complexity validation
- Secure password hashing (bcrypt)
- JWT with expiration
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import re
from jose import jwt
from uuid import UUID
import logging

from app.database import get_db
from app.models.user import User
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# Import rate limiter
try:
    from app.middleware.rate_limit import limiter, RateLimits
    RATE_LIMITING_ENABLED = True
except ImportError:
    RATE_LIMITING_ENABLED = False
    logger.warning("Rate limiting not available for auth endpoints")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    
    class Config:
        extra = "forbid"  # Reject unknown fields (mass assignment protection)
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Validate password meets complexity requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        extra = "forbid"  # Reject unknown fields


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool = False


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool = False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: str, email: str, is_admin: bool = False) -> str:
    """Create a JWT access token"""
    expires_delta = timedelta(days=settings.jwt_expire_days)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "is_admin": is_admin,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.REGISTER)
async def register(
    request: Request,  # Must be named 'request' and first for slowapi
    register_data: RegisterRequest = None,  # Will get from body
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Rate limited to 3 requests per minute to prevent abuse.
    """
    # Parse body manually since 'request' is taken by slowapi
    body = await request.json()
    register_data = RegisterRequest(**body)
    
    # Log registration attempt (for security monitoring)
    client_ip = getattr(request.state, 'client_ip', 'unknown')
    logger.info(f"Registration attempt for email: {register_data.email[:3]}*** from {client_ip}")
    
    # Validate passwords match
    if register_data.password != register_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Password complexity is now validated by Pydantic validator
    
    # Check if user already exists
    stmt = select(User).where(User.email == register_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(register_data.password)
    
    # Insert user with both hashed_password and password_hash (Supabase requires password_hash)
    from sqlalchemy import text
    from uuid import uuid4
    user_id = uuid4()
    
    await db.execute(
        text("""
            INSERT INTO users (id, email, hashed_password, password_hash, is_active, is_superuser, created_at)
            VALUES (:id, :email, :hashed_password, :password_hash, :is_active, :is_superuser, NOW())
        """),
        {
            "id": user_id,
            "email": register_data.email,
            "hashed_password": hashed_password,
            "password_hash": hashed_password,
            "is_active": True,
            "is_superuser": False
        }
    )
    await db.commit()
    
    # Get the created user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    new_user = result.scalar_one()
    
    return {"message": "User registered successfully", "email": new_user.email}


@router.post("/login", response_model=AuthResponse)
@limiter.limit(RateLimits.LOGIN)
async def login(
    request: Request,  # Must be named 'request' and first for slowapi
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token.
    
    Rate limited to 5 requests per minute to prevent brute force attacks.
    """
    # Parse body manually since 'request' is taken by slowapi
    body = await request.json()
    login_data = LoginRequest(**body)
    
    # Log login attempt (for security monitoring)
    client_ip = getattr(request.state, 'client_ip', 'unknown')
    
    # Find user by email
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Log failed attempt
        logger.warning(f"Login failed: unknown email attempt from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        logger.warning(f"Login failed: inactive account {login_data.email[:3]}*** from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        # Log failed attempt (but don't reveal which field was wrong)
        logger.warning(f"Login failed: invalid password for {login_data.email[:3]}*** from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Log successful login
    logger.info(f"Login successful: {login_data.email[:3]}*** from {client_ip}")
    
    # Create access token with admin status
    is_admin = user.is_superuser if user.is_superuser else False
    access_token = create_access_token(str(user.id), user.email, is_admin=is_admin)
    
    return AuthResponse(access_token=access_token, token_type="bearer", is_admin=is_admin)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    is_admin = current_user.is_superuser if current_user.is_superuser else False
    return UserResponse(id=str(current_user.id), email=current_user.email, is_admin=is_admin)

