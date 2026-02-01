"""
User Model
User authentication and profile information

Security Features:
- token_version: Incremented on password change, role change, or manual revocation
  All tokens with older version are automatically invalidated
- role: Stored in DB, fetched on each request (not trusted from JWT)
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional
import uuid
import enum

from app.models import Base


class UserRole(str, enum.Enum):
    """User roles for authorization"""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and profile"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # Legacy, use 'role' instead
    
    # Security: Role stored in DB, fetched on each request (not from JWT)
    role = Column(String, default=UserRole.USER.value, nullable=False)
    
    # Security: Token version for revocation
    # Increment this to invalidate all existing tokens for this user
    # Use cases: password change, role change, security concern, logout-all
    token_version = Column(Integer, default=1, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Subscription and trial fields
    trial_started_at = Column(DateTime(timezone=True), nullable=True)
    trial_ended_at = Column(DateTime(timezone=True), nullable=True)
    subscription_status = Column(String(20), default='trial', nullable=False)
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    discord_handle = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    auth_provider = Column(String(20), default='email', nullable=False)
    
    @property
    def is_admin(self) -> bool:
        """
        Check if user has admin role (from DB, not JWT).
        
        SECURITY: Only checks 'role' column - single source of truth.
        The legacy 'is_superuser' column is ignored to prevent accidental escalation.
        """
        return self.role == UserRole.ADMIN.value
    
    def invalidate_tokens(self):
        """Increment token_version to invalidate all existing tokens"""
        self.token_version = (self.token_version or 0) + 1
    
    def has_active_access(self) -> bool:
        """
        Check if user has active access (trial or subscription).
        Returns True if:
        - User is in trial period (trial_ended_at is in the future)
        - User has active subscription (subscription_status == 'active')
        - User has trial subscription from Stripe (subscription_status == 'trial')
        """
        # Pioneer users have full access
        if self.subscription_status == 'pioneer':
            return True

        # Check if trial is still active (based on trial_ended_at date)
        if self.trial_ended_at and self.trial_ended_at > datetime.utcnow():
            return True

        # Check if subscription is active (paid subscription)
        if self.subscription_status == 'active':
            return True

        # Check if subscription is in trial (Stripe trialing status)
        if self.subscription_status == 'trial':
            return True

        return False
    
    def days_remaining_in_trial(self) -> Optional[int]:
        """Calculate days remaining in trial period"""
        if not self.trial_ended_at:
            return None
        
        now = datetime.utcnow()
        if self.trial_ended_at <= now:
            return 0
        
        delta = self.trial_ended_at - now
        return delta.days
    
    def is_subscription_active(self) -> bool:
        """Check if user has an active subscription (not trial)"""
        return self.subscription_status == 'active'
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role}, status={self.subscription_status})>"
