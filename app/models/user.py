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
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # Legacy, use 'role' instead
    
    # Security: Role stored in DB, fetched on each request (not from JWT)
    role = Column(String, default=UserRole.USER.value, nullable=False)
    
    # Security: Token version for revocation
    # Increment this to invalidate all existing tokens for this user
    # Use cases: password change, role change, security concern, logout-all
    token_version = Column(Integer, default=1, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
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
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

