"""Add ranking fields to box_metrics_unified

Revision ID: 003
Revises: 001
Create Date: 2025-01-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns already exist (in case they were added manually)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('box_metrics_unified')]
    
    # Add current_rank - current rank position (1 = highest volume)
    if 'current_rank' not in columns:
        op.add_column('box_metrics_unified', 
                      sa.Column('current_rank', sa.Integer(), nullable=True))
    
    # Add previous_rank - previous day's rank (for rank change detection)
    if 'previous_rank' not in columns:
        op.add_column('box_metrics_unified',
                      sa.Column('previous_rank', sa.Integer(), nullable=True))
    
    # Check if index exists before creating
    indexes = [idx['name'] for idx in inspector.get_indexes('box_metrics_unified')]
    if 'idx_metrics_date_rank' not in indexes:
        # Add index on (metric_date, current_rank) for efficient leaderboard queries
        op.create_index('idx_metrics_date_rank', 'box_metrics_unified', 
                        ['metric_date', 'current_rank'], unique=False)


def downgrade() -> None:
    # Check if index exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    indexes = [idx['name'] for idx in inspector.get_indexes('box_metrics_unified')]
    
    # Remove index if it exists
    if 'idx_metrics_date_rank' in indexes:
        op.drop_index('idx_metrics_date_rank', table_name='box_metrics_unified')
    
    # Check if columns exist before dropping
    columns = [col['name'] for col in inspector.get_columns('box_metrics_unified')]
    
    # Remove columns if they exist
    if 'previous_rank' in columns:
        op.drop_column('box_metrics_unified', 'previous_rank')
    if 'current_rank' in columns:
        op.drop_column('box_metrics_unified', 'current_rank')

