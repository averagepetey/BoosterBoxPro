"""
User SQLAlchemy Model
Core entity for authentication and user management
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Boolean, Integer, TIMESTAMP, CheckConstraint, Enum, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import enum

from app.models import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SubscriptionStatusType(TypeDecorator):
    """Custom type to ensure enum values (not names) are stored"""
    impl = String
    cache_ok = True
    
    def __init__(self):
        super().__init__(20)
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, SubscriptionStatus):
            return value.value  # Return the value, not the name
        if isinstance(value, str):
            return value  # Already a string value
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value  # Return as string


class User(Base):
    """User model for authentication and subscription management"""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Subscription & Trial
    trial_started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    trial_ended_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    subscription_status: Mapped[str] = mapped_column(
        String(20),  # Database column is VARCHAR, enum enforced at application level
        nullable=False,
        server_default="trial",
        index=True
    )
    
    # Stripe Integration
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Security & Permissions
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true"
    )
    token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "subscription_status IN ('trial', 'active', 'expired', 'cancelled')",
            name="check_subscription_status"
        ),
    )
    
    def has_active_access(self) -> bool:
        """Check if user has active access (trial or subscription)"""
        from datetime import datetime, timezone
        
        # Check if subscription is active
        if self.subscription_status == "active":
            return True
        
        # Check if trial is active
        if self.subscription_status == "trial" and self.trial_ended_at:
            now = datetime.now(timezone.utc)
            if self.trial_ended_at > now:
                return True
        
        return False
    
    def days_remaining_in_trial(self) -> int:
        """Calculate days remaining in trial"""
        from datetime import datetime, timezone
        
        if not self.trial_ended_at:
            return 0
        
        now = datetime.now(timezone.utc)
        if self.trial_ended_at <= now:
            return 0
        
        delta = self.trial_ended_at - now
        return max(0, delta.days)
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        return self.subscription_status == "active"
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, status={self.subscription_status})>"
