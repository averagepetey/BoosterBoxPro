"""Add missing metric fields for automated screenshot processing

Revision ID: 002
Revises: 001
Create Date: 2025-01-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns already exist (in case they were added manually)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('box_metrics_unified')]
    
    # Add unified_volume_30d_sma - 30-day Simple Moving Average of volume
    if 'unified_volume_30d_sma' not in columns:
        op.add_column('box_metrics_unified', 
                      sa.Column('unified_volume_30d_sma', sa.Numeric(12, 2), nullable=True))
    
    # Add volume_mom_change_pct - Month-over-month volume change percentage
    if 'volume_mom_change_pct' not in columns:
        op.add_column('box_metrics_unified',
                      sa.Column('volume_mom_change_pct', sa.Numeric(6, 2), nullable=True))
    
    # Add avg_boxes_added_per_day - 30-day average of boxes added per day (capped at 30d avg)
    if 'avg_boxes_added_per_day' not in columns:
        op.add_column('box_metrics_unified',
                      sa.Column('avg_boxes_added_per_day', sa.Numeric(8, 2), nullable=True))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('box_metrics_unified', 'avg_boxes_added_per_day')
    op.drop_column('box_metrics_unified', 'volume_mom_change_pct')
    op.drop_column('box_metrics_unified', 'unified_volume_30d_sma')

