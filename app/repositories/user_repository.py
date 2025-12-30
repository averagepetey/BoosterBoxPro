"""
User Repository
Database operations for User model
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User, SubscriptionStatus
from app.utils.password import hash_password


class UserRepository:
    """Repository for User database operations"""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        email: str,
        password: str,
        username: Optional[str] = None,
        start_trial: bool = True,
        trial_days: int = 7
    ) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            username: Optional username
            start_trial: Whether to start a trial (default: True)
            trial_days: Number of days for trial (default: 7)
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = await UserRepository.get_by_email(db, email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        
        # Create user
        user = User(email=email, password=password, username=username)
        
        # Start trial if requested
        if start_trial:
            user.start_trial(days=trial_days)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User object or None if not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object or None if not found
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_stripe_customer_id(db: AsyncSession, stripe_customer_id: str) -> Optional[User]:
        """
        Get user by Stripe customer ID
        
        Args:
            db: Database session
            stripe_customer_id: Stripe customer ID
            
        Returns:
            User object or None if not found
        """
        result = await db.execute(
            select(User).where(User.stripe_customer_id == stripe_customer_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update(db: AsyncSession, user: User) -> User:
        """
        Update user in database
        
        Args:
            db: Database session
            user: User object with updated fields
            
        Returns:
            Updated User object
        """
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: UUID) -> None:
        """
        Update user's last login timestamp
        
        Args:
            db: Database session
            user_id: User UUID
        """
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.utcnow())
        )
        await db.commit()
    
    @staticmethod
    async def update_subscription_status(
        db: AsyncSession,
        user_id: UUID,
        status: SubscriptionStatus,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None
    ) -> User:
        """
        Update user's subscription status and Stripe IDs
        
        Args:
            db: Database session
            user_id: User UUID
            status: New subscription status
            stripe_customer_id: Optional Stripe customer ID
            stripe_subscription_id: Optional Stripe subscription ID
            
        Returns:
            Updated User object
        """
        update_values = {
            "subscription_status": status,
            "updated_at": datetime.utcnow()
        }
        
        if stripe_customer_id is not None:
            update_values["stripe_customer_id"] = stripe_customer_id
        
        if stripe_subscription_id is not None:
            update_values["stripe_subscription_id"] = stripe_subscription_id
        
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_values)
        )
        await db.commit()
        
        # Return updated user
        user = await UserRepository.get_by_id(db, user_id)
        return user

