"""
Script to view all users in the database
Usage: python scripts/view_users.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import create_async_engine, async_sessionmaker
from app.models.user import User
from sqlalchemy import select


async def view_users():
    """View all users in the database"""
    from app.config import settings
    
    # Create database connection
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Query all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(users)} user(s) in database:")
        print(f"{'='*80}\n")
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Username: {user.username or '(not set)'}")
            print(f"Subscription Status: {user.subscription_status.value if user.subscription_status else 'none'}")
            print(f"Trial Started: {user.trial_started_at}")
            print(f"Trial Ends: {user.trial_ended_at}")
            print(f"Created At: {user.created_at}")
            print(f"Last Login: {user.last_login_at or '(never)'}")
            print(f"{'-'*80}\n")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(view_users())

