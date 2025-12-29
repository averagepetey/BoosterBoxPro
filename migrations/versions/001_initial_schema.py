"""Initial schema - Create all core tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create booster_boxes table
    op.create_table(
        'booster_boxes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('external_product_id', sa.String(255), nullable=True, unique=True),  # Nullable for manual mode
        sa.Column('product_name', sa.String(500), nullable=False),
        sa.Column('set_name', sa.String(255), nullable=True),
        sa.Column('game_type', sa.String(100), nullable=True, server_default='One Piece'),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('estimated_total_supply', sa.Integer(), nullable=True),
        sa.Column('reprint_risk', sa.String(20), nullable=False, server_default='LOW'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("reprint_risk IN ('LOW', 'MEDIUM', 'HIGH')", name='check_reprint_risk'),
    )
    
    # Indexes for booster_boxes
    op.create_index('idx_external_product_id', 'booster_boxes', ['external_product_id'], unique=False)
    op.create_index('idx_game_type', 'booster_boxes', ['game_type'], unique=False)
    
    # Create tcg_listings_raw table (placeholder for future API integration)
    op.create_table(
        'tcg_listings_raw',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('listing_id', sa.String(255), nullable=False),
        sa.Column('seller_id', sa.String(255), nullable=True),
        sa.Column('listed_price_usd', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('snapshot_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('booster_box_id', 'listing_id', 'snapshot_date', name='uq_tcg_listing_date'),
        sa.CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    # Indexes for tcg_listings_raw
    op.create_index('idx_tcg_booster_box_date', 'tcg_listings_raw', ['booster_box_id', 'snapshot_date'], unique=False)
    op.create_index('idx_tcg_snapshot_date', 'tcg_listings_raw', ['snapshot_date'], unique=False)
    op.create_index('idx_tcg_listing_id', 'tcg_listings_raw', ['listing_id'], unique=False)
    
    # Create tcg_box_metrics_daily table
    op.create_table(
        'tcg_box_metrics_daily',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('floor_price_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('visible_market_cap_usd', sa.Numeric(12, 2), nullable=True),
        sa.Column('active_listings_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tcg_volume_usd', sa.Numeric(12, 2), nullable=True, server_default='0'),
        sa.Column('tcg_units_sold_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('boxes_added_today', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tcg_volume_7d_ema', sa.Numeric(12, 2), nullable=True),
        sa.Column('tcg_volume_30d_sma', sa.Numeric(12, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('booster_box_id', 'metric_date', name='uq_tcg_metrics_date'),
    )
    
    # Indexes for tcg_box_metrics_daily
    op.create_index('idx_tcg_metrics_box_date', 'tcg_box_metrics_daily', ['booster_box_id', 'metric_date'], unique=False)
    
    # Create ebay_sales_raw table (placeholder for future API integration)
    op.create_table(
        'ebay_sales_raw',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_date', sa.Date(), nullable=False),
        sa.Column('sale_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('ebay_item_id', sa.String(255), nullable=False),
        sa.Column('sold_price_usd', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('seller_id', sa.String(255), nullable=True),
        sa.Column('listing_type', sa.String(50), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('booster_box_id', 'ebay_item_id', name='uq_ebay_sale_item'),
    )
    
    # Indexes for ebay_sales_raw
    op.create_index('idx_ebay_booster_box_date', 'ebay_sales_raw', ['booster_box_id', 'sale_date'], unique=False)
    op.create_index('idx_ebay_sale_date', 'ebay_sales_raw', ['sale_date'], unique=False)
    op.create_index('idx_ebay_item_id', 'ebay_sales_raw', ['ebay_item_id'], unique=False)
    
    # Create ebay_box_metrics_daily table
    op.create_table(
        'ebay_box_metrics_daily',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('ebay_sales_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('ebay_volume_usd', sa.Numeric(12, 2), nullable=True, server_default='0'),
        sa.Column('ebay_median_sold_price_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('ebay_units_sold_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('ebay_sales_acceleration', sa.Numeric(8, 2), nullable=True),
        sa.Column('ebay_volume_7d_ema', sa.Numeric(12, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('booster_box_id', 'metric_date', name='uq_ebay_metrics_date'),
    )
    
    # Indexes for ebay_box_metrics_daily
    op.create_index('idx_ebay_metrics_box_date', 'ebay_box_metrics_daily', ['booster_box_id', 'metric_date'], unique=False)
    
    # Create box_metrics_unified table (PRIMARY table for leaderboard)
    op.create_table(
        'box_metrics_unified',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('floor_price_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('floor_price_1d_change_pct', sa.Numeric(6, 2), nullable=True),
        sa.Column('unified_volume_usd', sa.Numeric(12, 2), nullable=True, server_default='0'),
        sa.Column('unified_volume_7d_ema', sa.Numeric(12, 2), nullable=True),  # PRIMARY RANKING METRIC
        sa.Column('liquidity_score', sa.Numeric(8, 2), nullable=True),
        sa.Column('momentum_score', sa.Numeric(8, 2), nullable=True),
        sa.Column('boxes_sold_per_day', sa.Numeric(8, 2), nullable=True),
        sa.Column('boxes_sold_30d_avg', sa.Numeric(8, 2), nullable=True),
        sa.Column('active_listings_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('visible_market_cap_usd', sa.Numeric(12, 2), nullable=True),
        sa.Column('boxes_added_today', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('days_to_20pct_increase', sa.Numeric(8, 2), nullable=True),
        sa.Column('listed_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('expected_days_to_sell', sa.Numeric(8, 2), nullable=True),  # NEW: Expected days to sell metric
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('booster_box_id', 'metric_date', name='uq_unified_metrics_date'),
    )
    
    # Indexes for box_metrics_unified (critical for leaderboard queries)
    op.create_index('idx_unified_box_date', 'box_metrics_unified', ['booster_box_id', 'metric_date'], unique=False)
    # Create index for unified_volume_7d_ema (primary ranking metric)
    op.create_index('idx_unified_volume_7d_ema', 'box_metrics_unified', ['unified_volume_7d_ema'], unique=False)
    op.create_index('idx_metric_date', 'box_metrics_unified', ['metric_date'], unique=False)
    
    # Create tcg_listing_changes table (audit log)
    op.create_table(
        'tcg_listing_changes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('listing_id', sa.String(255), nullable=False),
        sa.Column('change_date', sa.Date(), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('previous_quantity', sa.Integer(), nullable=True),
        sa.Column('new_quantity', sa.Integer(), nullable=True),
        sa.Column('previous_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('new_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('detected_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.CheckConstraint("change_type IN ('LISTED', 'DELISTED', 'QUANTITY_DECREASED', 'QUANTITY_INCREASED', 'PRICE_CHANGED', 'RELISTED')", name='check_change_type'),
    )
    
    # Indexes for tcg_listing_changes
    op.create_index('idx_listing_changes_box_date', 'tcg_listing_changes', ['booster_box_id', 'change_date'], unique=False)
    op.create_index('idx_listing_changes_listing_id', 'tcg_listing_changes', ['listing_id'], unique=False)
    op.create_index('idx_listing_changes_date', 'tcg_listing_changes', ['change_date'], unique=False)
    
    # Create users table (for authentication and favorites)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=True, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_login_at', sa.TIMESTAMP(), nullable=True),
    )
    
    # Indexes for users
    op.create_index('idx_user_email', 'users', ['email'], unique=True)
    op.create_index('idx_user_username', 'users', ['username'], unique=False)
    
    # Create user_favorites table (many-to-many relationship)
    op.create_table(
        'user_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('booster_box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['booster_box_id'], ['booster_boxes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'booster_box_id', name='uq_user_favorite'),
    )
    
    # Indexes for user_favorites
    op.create_index('idx_user_favorites_user', 'user_favorites', ['user_id'], unique=False)
    op.create_index('idx_user_favorites_box', 'user_favorites', ['booster_box_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('user_favorites')
    op.drop_table('users')
    op.drop_table('tcg_listing_changes')
    op.drop_table('box_metrics_unified')
    op.drop_table('ebay_box_metrics_daily')
    op.drop_table('ebay_sales_raw')
    op.drop_table('tcg_box_metrics_daily')
    op.drop_table('tcg_listings_raw')
    op.drop_table('booster_boxes')

