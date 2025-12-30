"""Add performance indexes for Phase 5

Revision ID: 002
Revises: 001
Create Date: 2024-12-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add composite index for ranking queries on box_metrics_unified table.
    
    This index optimizes queries that:
    - Get leaderboard data for a specific date sorted by volume_7d_ema
    - Calculate rankings efficiently
    """
    # Composite index for ranking queries: (metric_date, unified_volume_7d_ema)
    # This is critical for Phase 6 ranking calculations
    # Query pattern: WHERE metric_date = X ORDER BY unified_volume_7d_ema DESC
    op.create_index(
        'idx_unified_date_volume_ema',
        'box_metrics_unified',
        ['metric_date', 'unified_volume_7d_ema'],
        unique=False,
        postgresql_ops={'unified_volume_7d_ema': 'DESC'}  # Optimize for DESC sorting
    )


def downgrade() -> None:
    """Remove the composite index"""
    op.drop_index('idx_unified_date_volume_ema', table_name='box_metrics_unified')

