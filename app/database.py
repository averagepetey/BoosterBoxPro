"""
Database Connection and Session Management
"""

import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.config import settings

# asyncpg does not accept 'sslmode' as a connect() kwarg; SQLAlchemy passes URL params through.
# Strip sslmode from URL and pass a proper SSL context via connect_args so Supabase/Render work.
# Supabase often requires CERT_NONE from server environments (Render) when default context fails.
_db_url = settings.database_url
_connect_args = {}
_needs_ssl = "sslmode=require" in _db_url or "supabase" in _db_url.lower()
if _needs_ssl:
    _ctx = ssl.create_default_context()
    if "supabase" in _db_url.lower():
        # SECURITY NOTE: Supabase pooler from Render/GH Actions fails cert verification.
        # This is a known tradeoff. The connection is still encrypted (TLS), just not
        # verifying the server certificate. Acceptable for Supabase pooler connections.
        _ctx.check_hostname = False
        _ctx.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = _ctx
if "sslmode=require" in _db_url:
    _db_url = _db_url.replace("?sslmode=require&", "?").replace("&sslmode=require", "").replace("?sslmode=require", "?")
    if _db_url.endswith("?"):
        _db_url = _db_url[:-1]

_engine_kw = dict(
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=3,
    max_overflow=2,
)
if _connect_args:
    _engine_kw["connect_args"] = _connect_args
engine = create_async_engine(_db_url, **_engine_kw)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session
    Used in FastAPI route dependencies
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database connection
    Can be used to test connection on startup
    """
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Test connection
        await conn.execute(text("SELECT 1"))
    print("✅ Database connection successful")

