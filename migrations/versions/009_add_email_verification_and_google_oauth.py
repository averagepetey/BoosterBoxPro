"""Add email_verified, google_id, auth_provider to users table

Revision ID: 009
Revises: 008
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]

    # Add email_verified column (default False for new users)
    if 'email_verified' not in columns:
        op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # Add google_id column (unique, nullable)
    if 'google_id' not in columns:
        op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
        op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True, postgresql_where=sa.text('google_id IS NOT NULL'))

    # Add auth_provider column
    if 'auth_provider' not in columns:
        op.add_column('users', sa.Column('auth_provider', sa.String(20), nullable=False, server_default='email'))

    # Make hashed_password nullable (Google OAuth users have no password)
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=True)

    # All existing users have verified emails (they're pioneers who registered with real emails)
    op.execute("UPDATE users SET email_verified = true WHERE email_verified = false")


def downgrade() -> None:
    # Set a placeholder password for any Google-only users before making column non-nullable
    op.execute("UPDATE users SET hashed_password = 'GOOGLE_OAUTH_NO_PASSWORD' WHERE hashed_password IS NULL")
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=False)

    try:
        op.drop_index('ix_users_google_id', table_name='users')
    except Exception:
        pass

    try:
        op.drop_column('users', 'auth_provider')
    except Exception:
        pass

    try:
        op.drop_column('users', 'google_id')
    except Exception:
        pass

    try:
        op.drop_column('users', 'email_verified')
    except Exception:
        pass
