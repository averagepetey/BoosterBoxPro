"""Add Phase 8 user fields for monetization

Revision ID: 004
Revises: 003
Create Date: 2024-12-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add Phase 8 fields to users table:
    - Trial dates (trial_started_at, trial_ended_at)
    - Subscription status (subscription_status ENUM)
    - Stripe IDs (stripe_customer_id, stripe_subscription_id)
    """
    # Create subscription_status ENUM type
    op.execute("""
        CREATE TYPE subscription_status_enum AS ENUM ('trial', 'active', 'expired', 'cancelled', 'none')
    """)
    
    # Add trial date columns
    op.add_column('users', sa.Column('trial_started_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('users', sa.Column('trial_ended_at', sa.TIMESTAMP(), nullable=True))
    
    # Add subscription status column
    op.add_column('users', sa.Column('subscription_status', sa.Enum('trial', 'active', 'expired', 'cancelled', 'none', name='subscription_status_enum'), nullable=True, server_default='none'))
    
    # Add Stripe columns
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
    
    # Add index for stripe_customer_id
    op.create_index('idx_user_stripe_customer_id', 'users', ['stripe_customer_id'], unique=True)
    
    # Update existing users to have 'none' subscription status
    op.execute("UPDATE users SET subscription_status = 'none' WHERE subscription_status IS NULL")


def downgrade() -> None:
    """Remove Phase 8 fields from users table"""
    # Drop index
    op.drop_index('idx_user_stripe_customer_id', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'trial_ended_at')
    op.drop_column('users', 'trial_started_at')
    
    # Drop ENUM type
    op.execute("DROP TYPE subscription_status_enum")

