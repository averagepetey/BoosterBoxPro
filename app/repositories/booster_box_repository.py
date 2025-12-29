"""
Booster Box Repository
Data access layer for booster box operations
"""

from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.booster_box import BoosterBox


class BoosterBoxRepository:
    """Repository for booster box database operations"""
    
    @staticmethod
    async def create(db: AsyncSession, box_data: dict) -> BoosterBox:
        """Create a new booster box"""
        box = BoosterBox(**box_data)
        db.add(box)
        await db.commit()
        await db.refresh(box)
        return box
    
    @staticmethod
    async def get_by_id(db: AsyncSession, box_id: UUID) -> Optional[BoosterBox]:
        """Get a booster box by ID"""
        result = await db.execute(select(BoosterBox).where(BoosterBox.id == box_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, limit: Optional[int] = None, offset: int = 0) -> List[BoosterBox]:
        """Get all booster boxes"""
        query = select(BoosterBox).offset(offset)
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_external_id(db: AsyncSession, external_id: str) -> Optional[BoosterBox]:
        """Get a booster box by external product ID"""
        result = await db.execute(
            select(BoosterBox).where(BoosterBox.external_product_id == external_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def count(db: AsyncSession) -> int:
        """Count total number of booster boxes"""
        from sqlalchemy import func
        result = await db.execute(select(func.count(BoosterBox.id)))
        return result.scalar() or 0

