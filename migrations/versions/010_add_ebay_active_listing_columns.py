"""Add ebay active listing columns to ebay_box_metrics_daily

Revision ID: 010
Revises: 009
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ebay_box_metrics_daily',
                  sa.Column('ebay_active_listings_count', sa.Integer(), nullable=True))
    op.add_column('ebay_box_metrics_daily',
                  sa.Column('ebay_active_median_price_usd', sa.Numeric(10, 2), nullable=True))
    op.add_column('ebay_box_metrics_daily',
                  sa.Column('ebay_active_low_price_usd', sa.Numeric(10, 2), nullable=True))
    op.add_column('ebay_box_metrics_daily',
                  sa.Column('ebay_listings_added_today', sa.Integer(), nullable=True))
    op.add_column('ebay_box_metrics_daily',
                  sa.Column('ebay_listings_removed_today', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('ebay_box_metrics_daily', 'ebay_listings_removed_today')
    op.drop_column('ebay_box_metrics_daily', 'ebay_listings_added_today')
    op.drop_column('ebay_box_metrics_daily', 'ebay_active_low_price_usd')
    op.drop_column('ebay_box_metrics_daily', 'ebay_active_median_price_usd')
    op.drop_column('ebay_box_metrics_daily', 'ebay_active_listings_count')
