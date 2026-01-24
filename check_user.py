"""
Script to check if a user exists in the database
"""
import asyncio
import sys
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole

async def check_user(email: str):
    """Check if a user exists and display their info"""
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ User found: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Role: {user.role}")
                print(f"   Is Admin: {user.is_admin}")
                print(f"   Is Active: {user.is_active}")
                print(f"   Token Version: {user.token_version}")
                print(f"   Created At: {user.created_at}")
                print(f"\n📦 Subscription Info:")
                print(f"   Status: {user.subscription_status}")
                print(f"   Stripe Customer ID: {user.stripe_customer_id or 'Not set'}")
                print(f"   Stripe Subscription ID: {user.stripe_subscription_id or 'Not set'}")
                if user.trial_started_at:
                    print(f"   Trial Started: {user.trial_started_at}")
                if user.trial_ended_at:
                    print(f"   Trial Ends: {user.trial_ended_at}")
                    from datetime import datetime
                    if user.trial_ended_at > datetime.utcnow():
                        days_left = (user.trial_ended_at - datetime.utcnow()).days
                        print(f"   Days Remaining: {days_left}")
            else:
                print(f"❌ User not found: {email}")
                print("\nListing all users in database:")
                all_users_stmt = select(User)
                all_result = await db.execute(all_users_stmt)
                all_users = all_result.scalars().all()
                if all_users:
                    for u in all_users:
                        print(f"   - {u.email} (role: {u.role}, active: {u.is_active})")
                else:
                    print("   No users found in database")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "john.petersen1818@gmail.com"
    print(f"Checking for user: {email}\n")
    asyncio.run(check_user(email))

