"""
BoosterBox SQLAlchemy Model
Core entity representing a booster box product
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Integer, Date, CheckConstraint, Column, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class BoosterBox(Base):
    """Booster box product master data"""
    
    __tablename__ = "booster_boxes"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    
    # External product ID (nullable for manual mode)
    external_product_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )
    
    # Product information
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    set_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    game_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        server_default="One Piece",
        index=True
    )
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Supply and risk
    estimated_total_supply: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reprint_risk: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="LOW"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships (will be added when other models are created)
    # unified_metrics: Mapped[list["UnifiedBoxMetrics"]] = relationship(back_populates="booster_box")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "reprint_risk IN ('LOW', 'MEDIUM', 'HIGH')",
            name="check_reprint_risk"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<BoosterBox(id={self.id}, product_name='{self.product_name}', game_type='{self.game_type}')>"

