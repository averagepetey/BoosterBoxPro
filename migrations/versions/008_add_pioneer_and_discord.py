"""Add pioneer subscription status and discord_handle to users table

Revision ID: 008
Revises: 007
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]

    # Add discord_handle column
    if 'discord_handle' not in columns:
        op.add_column('users', sa.Column('discord_handle', sa.String(255), nullable=True))

    # Update check constraint to include 'pioneer'
    # Drop old constraint first, then recreate with new values
    constraints = [c['name'] for c in inspector.get_check_constraints('users')]
    if 'check_subscription_status' in constraints:
        op.drop_constraint('check_subscription_status', 'users', type_='check')

    op.create_check_constraint(
        'check_subscription_status',
        'users',
        "subscription_status IN ('trial', 'active', 'expired', 'cancelled', 'pioneer')"
    )

    # Migrate existing trial users to pioneer
    op.execute("""
        UPDATE users
        SET subscription_status = 'pioneer'
        WHERE subscription_status = 'trial'
    """)


def downgrade() -> None:
    # Revert pioneer users back to trial
    op.execute("""
        UPDATE users
        SET subscription_status = 'trial'
        WHERE subscription_status = 'pioneer'
    """)

    # Restore original check constraint
    try:
        op.drop_constraint('check_subscription_status', 'users', type_='check')
    except Exception:
        pass

    op.create_check_constraint(
        'check_subscription_status',
        'users',
        "subscription_status IN ('trial', 'active', 'expired', 'cancelled')"
    )

    # Remove discord_handle column
    try:
        op.drop_column('users', 'discord_handle')
    except Exception:
        pass
