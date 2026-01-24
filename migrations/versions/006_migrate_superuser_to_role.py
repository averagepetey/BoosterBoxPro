"""Migrate is_superuser to role column (single source of truth)

SECURITY: This migration ensures any users with is_superuser=True
also have role='admin'. Going forward, only 'role' is checked for
admin access, preventing privilege escalation via the legacy column.

Revision ID: 006
Revises: 005
Create Date: 2026-01-21
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Sync is_superuser to role: anyone with is_superuser=True gets role='admin'
    op.execute("""
        UPDATE users 
        SET role = 'admin' 
        WHERE is_superuser = true AND role != 'admin'
    """)
    
    # Note: We keep is_superuser column for now (backwards compatibility)
    # but it's no longer checked in application code.
    # In a future migration, you can drop it entirely:
    # op.drop_column('users', 'is_superuser')


def downgrade():
    # No-op: we don't want to accidentally remove admin access
    pass


SECURITY: This migration ensures any users with is_superuser=True
also have role='admin'. Going forward, only 'role' is checked for
admin access, preventing privilege escalation via the legacy column.

Revision ID: 006
Revises: 005
Create Date: 2026-01-21
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Sync is_superuser to role: anyone with is_superuser=True gets role='admin'
    op.execute("""
        UPDATE users 
        SET role = 'admin' 
        WHERE is_superuser = true AND role != 'admin'
    """)
    
    # Note: We keep is_superuser column for now (backwards compatibility)
    # but it's no longer checked in application code.
    # In a future migration, you can drop it entirely:
    # op.drop_column('users', 'is_superuser')


def downgrade():
    # No-op: we don't want to accidentally remove admin access
    pass


SECURITY: This migration ensures any users with is_superuser=True
also have role='admin'. Going forward, only 'role' is checked for
admin access, preventing privilege escalation via the legacy column.

Revision ID: 006
Revises: 005
Create Date: 2026-01-21
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Sync is_superuser to role: anyone with is_superuser=True gets role='admin'
    op.execute("""
        UPDATE users 
        SET role = 'admin' 
        WHERE is_superuser = true AND role != 'admin'
    """)
    
    # Note: We keep is_superuser column for now (backwards compatibility)
    # but it's no longer checked in application code.
    # In a future migration, you can drop it entirely:
    # op.drop_column('users', 'is_superuser')


def downgrade():
    # No-op: we don't want to accidentally remove admin access
    pass


