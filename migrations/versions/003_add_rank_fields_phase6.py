"""Add rank fields for Phase 6

Revision ID: 003
Revises: 002
Create Date: 2024-12-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add rank fields to box_metrics_unified table for Phase 6 rankings.
    
    Fields:
    - current_rank: Current rank position (1 = highest volume)
    - previous_rank: Previous period's rank (for rank change detection)
    - rank_change: Change in rank (positive = moved up, negative = moved down)
    """
    # Add rank fields
    op.add_column('box_metrics_unified', sa.Column('current_rank', sa.Integer(), nullable=True))
    op.add_column('box_metrics_unified', sa.Column('previous_rank', sa.Integer(), nullable=True))
    op.add_column('box_metrics_unified', sa.Column('rank_change', sa.Integer(), nullable=True))
    
    # Add index for leaderboard queries: (metric_date, current_rank)
    # This optimizes queries that get top N boxes ordered by rank
    op.create_index(
        'idx_unified_date_rank',
        'box_metrics_unified',
        ['metric_date', 'current_rank'],
        unique=False
    )


def downgrade() -> None:
    """Remove rank fields and index"""
    op.drop_index('idx_unified_date_rank', table_name='box_metrics_unified')
    op.drop_column('box_metrics_unified', 'rank_change')
    op.drop_column('box_metrics_unified', 'previous_rank')
    op.drop_column('box_metrics_unified', 'current_rank')

