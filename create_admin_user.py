"""
Script to create an admin user or check existing users
"""
import asyncio
import sys
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.routers.auth import hash_password
from datetime import datetime, timezone, timedelta

async def create_admin_user(email: str, password: str):
    """Create an admin user"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ User already exists: {email}")
                print(f"   ID: {existing_user.id}")
                print(f"   Role: {existing_user.role}")
                print(f"   Is Admin: {existing_user.is_admin}")
                print(f"   Is Active: {existing_user.is_active}")
                
                # Update to admin if not already
                if existing_user.role != UserRole.ADMIN.value:
                    print(f"\n⚠️  User is not an admin. Updating to admin...")
                    existing_user.role = UserRole.ADMIN.value
                    await db.commit()
                    await db.refresh(existing_user)
                    print(f"✅ User updated to admin role")
                else:
                    print(f"✅ User is already an admin")
                
                return existing_user
            else:
                # Create new admin user
                print(f"Creating new admin user: {email}")
                hashed_password = hash_password(password)
                now = datetime.now(timezone.utc)
                trial_end = now + timedelta(days=7)
                
                new_user = User(
                    email=email,
                    hashed_password=hashed_password,
                    is_active=True,
                    role=UserRole.ADMIN.value,
                    token_version=1,
                    trial_started_at=now,
                    trial_ended_at=trial_end,
                    subscription_status="trial"
                )
                
                db.add(new_user)
                await db.commit()
                await db.refresh(new_user)
                
                print(f"✅ Admin user created successfully!")
                print(f"   ID: {new_user.id}")
                print(f"   Email: {new_user.email}")
                print(f"   Role: {new_user.role}")
                print(f"   Is Admin: {new_user.is_admin}")
                
                return new_user
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise

async def list_all_users():
    """List all users in the database"""
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(User)
            result = await db.execute(stmt)
            users = result.scalars().all()
            
            if users:
                print(f"\n📋 Found {len(users)} user(s) in database:\n")
                for user in users:
                    print(f"   Email: {user.email}")
                    print(f"   Role: {user.role} (Admin: {user.is_admin})")
                    print(f"   Active: {user.is_active}")
                    print(f"   Created: {user.created_at}")
                    print()
            else:
                print("❌ No users found in database")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        asyncio.run(list_all_users())
    else:
        email = sys.argv[1] if len(sys.argv) > 1 else "john.petersen1818@gmail.com"
        password = sys.argv[2] if len(sys.argv) > 2 else "Admin123!"
        
        print(f"Creating/checking admin user: {email}\n")
        asyncio.run(create_admin_user(email, password))

