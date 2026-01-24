"""Add security columns: role and token_version

Revision ID: 005
Revises: 004
Create Date: 2026-01-21

Security improvements:
- role: Store user role in DB (not in JWT) for secure authorization
- token_version: For token revocation on password change, role change, etc.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column if it doesn't exist
    conn = op.get_bind()
    
    # Check if columns exist before adding
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'role' not in columns:
        op.add_column('users', sa.Column('role', sa.String(), nullable=True))
        # Set default role for existing users
        op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
        # Set admin role for superusers
        op.execute("UPDATE users SET role = 'admin' WHERE is_superuser = true")
        # Make column not nullable after setting defaults
        op.alter_column('users', 'role', nullable=False, server_default='user')
    
    if 'token_version' not in columns:
        op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=True))
        # Set default token_version for existing users
        op.execute("UPDATE users SET token_version = 1 WHERE token_version IS NULL")
        # Make column not nullable after setting defaults
        op.alter_column('users', 'token_version', nullable=False, server_default='1')


def downgrade() -> None:
    # Remove columns
    op.drop_column('users', 'token_version')
    op.drop_column('users', 'role')
