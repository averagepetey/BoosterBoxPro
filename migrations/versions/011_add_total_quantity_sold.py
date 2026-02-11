"""Add total_quantity_sold column for daily delta tracking

Revision ID: 011
Revises: 010
Create Date: 2026-02-10

Stores the lifetime total units sold from TCGPlayer so we can compute
daily sales by simple subtraction: today_total - yesterday_total.
"""
from alembic import op
import sqlalchemy as sa

revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('box_metrics_unified',
                  sa.Column('total_quantity_sold', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('box_metrics_unified', 'total_quantity_sold')
