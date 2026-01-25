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
down_revision = '006'  # Migrates after 006_migrate_superuser_to_role
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check which columns already exist (some may have been added in earlier migrations)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Add subscription and trial fields (only if they don't exist)
    if 'trial_started_at' not in columns:
        op.add_column('users', sa.Column('trial_started_at', sa.TIMESTAMP(timezone=True), nullable=True))
    if 'trial_ended_at' not in columns:
        op.add_column('users', sa.Column('trial_ended_at', sa.TIMESTAMP(timezone=True), nullable=True))
    if 'subscription_status' not in columns:
        op.add_column('users', sa.Column('subscription_status', sa.String(20), nullable=False, server_default='trial'))
    if 'stripe_customer_id' not in columns:
        op.add_column('users', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    if 'stripe_subscription_id' not in columns:
        op.add_column('users', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
    if 'last_login_at' not in columns:
        op.add_column('users', sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True))
    
    # Note: is_active, token_version, and role were added in migrations 004 and 005
    # is_admin doesn't exist in the model (we use 'role' instead)
    
    # Add indexes (only if they don't exist)
    indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    if 'idx_user_subscription_status' not in indexes:
        op.create_index('idx_user_subscription_status', 'users', ['subscription_status'], unique=False)
    if 'idx_user_stripe_customer' not in indexes:
        op.create_index('idx_user_stripe_customer', 'users', ['stripe_customer_id'], unique=True)
    
    # Before adding constraint, ensure all existing rows have valid subscription_status values
    # This handles the case where subscription_status column already exists with invalid values
    if 'subscription_status' in columns:
        op.execute("""
            UPDATE users 
            SET subscription_status = 'trial' 
            WHERE subscription_status IS NULL 
               OR subscription_status NOT IN ('trial', 'active', 'expired', 'cancelled')
        """)
    
    # Add constraint (only if it doesn't exist)
    constraints = [c['name'] for c in inspector.get_check_constraints('users')]
    if 'check_subscription_status' not in constraints:
        op.create_check_constraint(
            'check_subscription_status',
            'users',
            "subscription_status IN ('trial', 'active', 'expired', 'cancelled')"
        )


def downgrade() -> None:
    # Remove constraint
    try:
        op.drop_constraint('check_subscription_status', 'users', type_='check')
    except:
        pass  # Constraint might not exist
    
    # Remove indexes
    try:
        op.drop_index('idx_user_stripe_customer', table_name='users')
    except:
        pass
    try:
        op.drop_index('idx_user_subscription_status', table_name='users')
    except:
        pass
    
    # Remove columns (only subscription-related, not is_active/token_version which are from earlier migrations)
    try:
        op.drop_column('users', 'last_login_at')
    except:
        pass
    try:
        op.drop_column('users', 'stripe_subscription_id')
    except:
        pass
    try:
        op.drop_column('users', 'stripe_customer_id')
    except:
        pass
    try:
        op.drop_column('users', 'subscription_status')
    except:
        pass
    try:
        op.drop_column('users', 'trial_ended_at')
    except:
        pass
    try:
        op.drop_column('users', 'trial_started_at')
    except:
        pass

