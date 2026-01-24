"""Add subscription and trial fields to users table

Revision ID: 007
Revises: 006
Create Date: 2026-01-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '003'  # Latest non-empty migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add subscription and trial fields
    op.add_column('users', sa.Column('trial_started_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('users', sa.Column('trial_ended_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(20), nullable=False, server_default='trial'))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add indexes
    op.create_index('idx_user_subscription_status', 'users', ['subscription_status'], unique=False)
    op.create_index('idx_user_stripe_customer', 'users', ['stripe_customer_id'], unique=True)
    
    # Add constraint
    op.create_check_constraint(
        'check_subscription_status',
        'users',
        "subscription_status IN ('trial', 'active', 'expired', 'cancelled')"
    )


def downgrade() -> None:
    # Remove constraint
    op.drop_constraint('check_subscription_status', 'users', type_='check')
    
    # Remove indexes
    op.drop_index('idx_user_stripe_customer', table_name='users')
    op.drop_index('idx_user_subscription_status', table_name='users')
    
    # Remove columns
    op.drop_column('users', 'token_version')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'trial_ended_at')
    op.drop_column('users', 'trial_started_at')

