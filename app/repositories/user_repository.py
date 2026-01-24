"""
User Repository
Data access layer for user operations
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, SubscriptionStatus
from app.utils.password import hash_password


class UserRepository:
    """Repository for user data access operations"""
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password: str,
        username: Optional[str] = None
    ) -> User:
        """
        Create a new user with hashed password
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            username: Optional username
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = await UserRepository.get_user_by_email(db, email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone.utc)
        trial_end = now + timedelta(days=7)
        
        user = User(
            email=email,
            username=username,
            hashed_password=password_hash,
            trial_started_at=now,
            trial_ended_at=trial_end,
            subscription_status=SubscriptionStatus.TRIAL.value,
            is_admin=False,
            is_active=True,
            token_version=1
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User) -> User:
        """
        Update user in database
        
        Args:
            db: Database session
            user: User object with updated fields
            
        Returns:
            Updated User object
        """
        await db.commit()
        await db.refresh(user)
        return user

