"""
User Model for Authentication and Subscription Management
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base
from app.utils.password import hash_password, verify_password
import enum


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    NONE = "none"
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class User(Base):
    """User model for authentication and subscription management"""
    
    __tablename__ = "users"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, server_default=func.gen_random_uuid())
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)  # Column name in DB is 'password_hash' per migration 001
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP, nullable=True)
    
    # Phase 8: Trial and Subscription fields
    trial_started_at = Column(TIMESTAMP, nullable=True)
    trial_ended_at = Column(TIMESTAMP, nullable=True)
    subscription_status = Column(SQLEnum(SubscriptionStatus, name='subscription_status_enum', create_type=False, values_callable=lambda x: [e.value for e in x]), nullable=True, default=SubscriptionStatus.NONE, server_default='none')
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Relationships
    # favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, email: str, password: str, username: Optional[str] = None, **kwargs):
        """Create a new user with hashed password"""
        super().__init__(**kwargs)
        self.email = email
        self.username = username
        self.password_hash = hash_password(password)
        self.subscription_status = SubscriptionStatus.NONE
    
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return verify_password(password, self.password_hash)
    
    def set_password(self, password: str) -> None:
        """
        Update the user's password
        
        Args:
            password: New plain text password to hash and store
        """
        self.password_hash = hash_password(password)
    
    def is_trial_active(self) -> bool:
        """
        Check if the user's trial is currently active
        
        Returns:
            True if trial is active, False otherwise
        """
        if not self.trial_started_at or not self.trial_ended_at:
            return False
        
        now = datetime.utcnow()
        return self.trial_started_at <= now <= self.trial_ended_at
    
    def days_remaining_in_trial(self) -> int:
        """
        Get the number of days remaining in the trial
        
        Returns:
            Number of days remaining (0 if trial expired or not started)
        """
        if not self.trial_ended_at:
            return 0
        
        now = datetime.utcnow()
        if now > self.trial_ended_at:
            return 0
        
        delta = self.trial_ended_at - now
        return max(0, delta.days)
    
    def is_subscription_active(self) -> bool:
        """
        Check if the user has an active paid subscription
        
        Returns:
            True if subscription is active, False otherwise
        """
        return self.subscription_status == SubscriptionStatus.ACTIVE
    
    def has_active_access(self) -> bool:
        """
        Check if the user has active access (either trial or subscription)
        
        Returns:
            True if user has active access, False otherwise
        """
        return self.is_trial_active() or self.is_subscription_active()
    
    def start_trial(self, days: int = 7) -> None:
        """
        Start a trial period for the user
        
        Args:
            days: Number of days for the trial (default: 7)
        """
        now = datetime.utcnow()
        self.trial_started_at = now
        self.trial_ended_at = now + timedelta(days=days)
        self.subscription_status = SubscriptionStatus.TRIAL
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, status={self.subscription_status})>"

