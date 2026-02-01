"""
Authentication Router
Handles user registration, login, and authentication

Security Features:
- Rate limiting on auth endpoints
- Password complexity validation
- Secure password hashing (bcrypt)
- JWT with proper claims (iss, aud, iat, exp, jti)
- Token version for revocation (password change, role change, logout-all)
- Admin role fetched from DB on each request (NOT from JWT)
- Short token expiry recommended (30 min) with refresh tokens
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import re
from jose import jwt, JWTError
from uuid import UUID, uuid4
import logging
import os
import secrets

from app.database import get_db
from app.models.user import User, UserRole
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# JWT Configuration - these should match your domain
JWT_ISSUER = "boosterboxpro"
JWT_AUDIENCE = "boosterboxpro-api"

# Import rate limiter
try:
    from app.middleware.rate_limit import limiter, RateLimits
    RATE_LIMITING_ENABLED = True
except ImportError:
    RATE_LIMITING_ENABLED = False
    # Create a dummy limiter decorator that does nothing
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()
    RateLimits = type('RateLimits', (), {'LOGIN': '5/minute', 'REGISTER': '3/minute'})()
    logger.warning("Rate limiting not available for auth endpoints - using dummy limiter")


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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    class Config:
        extra = "forbid"

    @field_validator('new_password')
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    class Config:
        extra = "forbid"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str

    class Config:
        extra = "forbid"

    @field_validator('new_password')
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class GoogleAuthRequest(BaseModel):
    credential: str
    class Config:
        extra = "forbid"


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool = False
    subscription_status: str = "inactive"
    discord_handle: Optional[str] = None
    created_at: Optional[str] = None
    email_verified: bool = False
    auth_provider: str = "email"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: str, token_version: int = 1) -> str:
    """
    Create a JWT access token.
    
    SECURITY: JWT does NOT contain is_admin or role.
    Admin status is fetched from DB on each request to prevent:
    - Stale permissions after role change
    - Token theft escalation
    - Algorithm confusion attacks giving admin access
    
    Claims:
    - sub: User ID (UUID)
    - iss: Token issuer
    - aud: Token audience
    - iat: Issued at timestamp
    - exp: Expiration timestamp
    - jti: Unique token ID (for revocation tracking)
    - tv: Token version (for bulk revocation)
    """
    now = datetime.utcnow()
    expires_delta = timedelta(hours=24)
    expire = now + expires_delta
    
    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),  # Unique token ID
        "tv": token_version,  # Token version for revocation
    }
    
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token with full claim validation.
    
    Validates:
    - Signature
    - Expiration (exp)
    - Issuer (iss)
    - Audience (aud)
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def create_purpose_token(user_id: str, purpose: str, expires_minutes: int) -> str:
    """Create a short-lived JWT for a specific purpose (password_reset, email_verification)."""
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "purpose": purpose,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_purpose_token(token: str, expected_purpose: str) -> str:
    """Decode a purpose token and return the user_id. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"verify_exp": True, "verify_iss": True, "verify_aud": True},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="This link has expired. Please request a new one.")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired link.")

    if payload.get("purpose") != expected_purpose:
        raise HTTPException(status_code=400, detail="Invalid link.")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid link.")
    return user_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from token.
    
    SECURITY:
    - Validates token_version against DB (revocation support)
    - Admin/role is fetched from DB, NOT from JWT
    - User must be active
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    token_version = payload.get("tv", 0)
    
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
    
    # SECURITY: Validate token version for revocation support
    # If user's token_version is higher than token's tv claim,
    # this token was issued before a security event (password change, etc.)
    db_token_version = user.token_version or 1
    if token_version < db_token_version:
        logger.warning(f"Revoked token used for user {user.id} (tv={token_version} < db={db_token_version})")
        raise HTTPException(
            status_code=401, 
            detail="Token has been revoked. Please login again."
        )
    
    return user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role for endpoint access.
    
    SECURITY: Admin status is checked from DB, not JWT.
    This prevents escalation via JWT manipulation.
    """
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.id} attempted admin access")
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


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

    # Pioneer program: free access, no trial timer
    new_user = User(
        email=register_data.email,
        hashed_password=hashed_password,
        is_active=True,
        role=UserRole.USER.value,
        token_version=1,
        subscription_status="pioneer"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send verification email (fire-and-forget — don't block registration)
    try:
        from app.services.email_service import send_verification_email
        token = create_purpose_token(str(new_user.id), "email_verification", expires_minutes=1440)
        send_verification_email(new_user.email, token)
    except Exception as e:
        logger.warning(f"Failed to send verification email during registration: {e}")

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
    try:
        body = await request.json()
        logger.debug(f"Login request body: {body}")
    except Exception as e:
        logger.error(f"Failed to parse request body: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body. Expected JSON with 'email' and 'password' fields."
        )
    
    # Validate request body
    if not body:
        logger.warning("Empty request body received for login")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is required. Please provide 'email' and 'password' fields."
        )
    
    try:
        login_data = LoginRequest(**body)
    except ValidationError as e:
        logger.error(f"Failed to validate login request: {e}")
        # Extract missing fields from Pydantic validation errors
        missing_fields = []
        for error in e.errors():
            if error['type'] == 'missing':
                field_name = error['loc'][-1] if error['loc'] else 'unknown'
                missing_fields.append(field_name)
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request format. Please provide 'email' and 'password' fields."
        )
    except Exception as e:
        logger.error(f"Unexpected error validating login request: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request format. Please provide 'email' and 'password' fields."
        )
    
    # Log login attempt (for security monitoring)
    client_ip = getattr(request.state, 'client_ip', 'unknown')
    
    # Find user by email
    try:
        stmt = select(User).where(User.email == login_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    except Exception as db_error:
        logger.error(f"Database error during login for {login_data.email[:3]}***: {str(db_error)}")
        # Try to refresh the database connection
        try:
            await db.rollback()
            # Retry the query
            stmt = select(User).where(User.email == login_data.email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
        except Exception as retry_error:
            logger.error(f"Database retry failed: {str(retry_error)}")
            detail = "Database connection error. Please try again."
            if os.environ.get("DEBUG_DB_ERROR"):
                detail += f" (Debug: {retry_error!s})"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )
    
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
    
    # Google-only users have no password — return same generic error
    if not user.hashed_password:
        logger.warning(f"Login failed: Google-only account {login_data.email[:3]}*** attempted password login from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
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
    
    # Create access token (NO is_admin in token - fetched from DB on each request)
    token_version = user.token_version or 1
    access_token = create_access_token(str(user.id), token_version)
    
    # Return is_admin for frontend UI (but not trusted for authorization)
    # Authorization is always checked server-side from DB
    is_admin = user.is_admin  # Uses property that checks DB role
    
    return AuthResponse(access_token=access_token, token_type="bearer", is_admin=is_admin)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information (admin status from DB)"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_admin=current_user.is_admin,
        subscription_status=current_user.subscription_status or "inactive",
        discord_handle=current_user.discord_handle,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        email_verified=current_user.email_verified,
        auth_provider=current_user.auth_provider or "email",
    )


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change the current user's password.

    Validates current password, enforces complexity on new password,
    invalidates all existing tokens, and returns a fresh access token.
    """
    body = await request.json()
    data = ChangePasswordRequest(**body)

    if data.new_password != data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )

    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = hash_password(data.new_password)
    current_user.invalidate_tokens()
    await db.commit()
    await db.refresh(current_user)

    token = create_access_token(str(current_user.id), current_user.token_version)
    return AuthResponse(access_token=token, token_type="bearer", is_admin=current_user.is_admin)


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Send a password reset email. Always returns success to prevent email enumeration."""
    body = await request.json()
    data = ForgotPasswordRequest(**body)

    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user and user.is_active:
        token = create_purpose_token(str(user.id), "password_reset", expires_minutes=15)
        try:
            from app.services.email_service import send_password_reset_email
            send_password_reset_email(user.email, token)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a token from the reset email."""
    body = await request.json()
    data = ResetPasswordRequest(**body)

    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user_id = decode_purpose_token(data.token, "password_reset")

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reset link.")

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid reset link.")

    user.hashed_password = hash_password(data.new_password)
    user.invalidate_tokens()
    await db.commit()

    return {"message": "Password has been reset successfully. Please log in with your new password."}


@router.post("/verify-email")
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify email address using a token from the verification email."""
    body = await request.json()
    token = body.get("token", "")

    if not token:
        raise HTTPException(status_code=400, detail="Token is required.")

    user_id = decode_purpose_token(token, "email_verification")

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid verification link.")

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification link.")

    user.email_verified = True
    await db.commit()

    return {"message": "Email verified successfully.", "email_verified": True}


@router.post("/resend-verification")
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resend verification email to the authenticated user."""
    if current_user.email_verified:
        return {"message": "Email is already verified."}

    token = create_purpose_token(str(current_user.id), "email_verification", expires_minutes=1440)
    try:
        from app.services.email_service import send_verification_email
        send_verification_email(current_user.email, token)
    except Exception as e:
        logger.error(f"Failed to resend verification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email.")

    return {"message": "Verification email sent."}


@router.post("/google", response_model=AuthResponse)
@limiter.limit("10/minute")
async def google_auth(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with a Google ID token. Creates account if needed."""
    body = await request.json()
    data = GoogleAuthRequest(**body)

    # Verify the Google ID token
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests

        if not settings.google_client_id:
            raise HTTPException(status_code=500, detail="Google OAuth is not configured")

        idinfo = google_id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as e:
        logger.warning(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_sub = idinfo.get("sub")
    email = idinfo.get("email")
    email_verified_by_google = idinfo.get("email_verified", False)

    if not email or not google_sub:
        raise HTTPException(status_code=401, detail="Google account missing email")

    # 1. Check if user exists by google_id
    stmt = select(User).where(User.google_id == google_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # 2. Check if user exists by email (link Google to existing account)
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.google_id = google_sub
            if email_verified_by_google:
                user.email_verified = True
            await db.commit()
            await db.refresh(user)
        else:
            # 3. Create new user
            user = User(
                email=email,
                hashed_password=None,
                is_active=True,
                role=UserRole.USER.value,
                token_version=1,
                subscription_status="pioneer",
                email_verified=email_verified_by_google,
                google_id=google_sub,
                auth_provider="google",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")

    token_version = user.token_version or 1
    access_token = create_access_token(str(user.id), token_version)

    return AuthResponse(access_token=access_token, token_type="bearer", is_admin=user.is_admin)
