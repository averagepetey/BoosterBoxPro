"""Add users table for authentication

Revision ID: 004
Revises: 003
Create Date: 2025-01-03

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
    # Check if table already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        # Create users table
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('email', sa.String(), nullable=False, unique=True),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )
    else:
        # Table exists - check and add missing columns
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'hashed_password' not in columns:
            op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
            # Update any existing rows with a placeholder (they'll need to reset password)
            op.execute("UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL")
            op.alter_column('users', 'hashed_password', nullable=False)
        
        if 'is_active' not in columns:
            op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
        
        if 'is_superuser' not in columns:
            op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
        
        if 'created_at' not in columns:
            op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        
        if 'updated_at' not in columns:
            op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Check if indexes exist before creating
    indexes = [idx['name'] for idx in inspector.get_indexes('users')] if 'users' in tables or 'users' not in tables else []
    
    if 'ix_users_id' not in indexes:
        try:
            op.create_index('ix_users_id', 'users', ['id'], unique=False)
        except Exception:
            pass  # Index might already exist
    
    if 'ix_users_email' not in indexes:
        try:
            op.create_index('ix_users_email', 'users', ['email'], unique=True)
        except Exception:
            pass  # Index might already exist


def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')


Revision ID: 004
Revises: 003
Create Date: 2025-01-03

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
    # Check if table already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        # Create users table
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('email', sa.String(), nullable=False, unique=True),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )
    else:
        # Table exists - check and add missing columns
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'hashed_password' not in columns:
            op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
            # Update any existing rows with a placeholder (they'll need to reset password)
            op.execute("UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL")
            op.alter_column('users', 'hashed_password', nullable=False)
        
        if 'is_active' not in columns:
            op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
        
        if 'is_superuser' not in columns:
            op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
        
        if 'created_at' not in columns:
            op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        
        if 'updated_at' not in columns:
            op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Check if indexes exist before creating
    indexes = [idx['name'] for idx in inspector.get_indexes('users')] if 'users' in tables or 'users' not in tables else []
    
    if 'ix_users_id' not in indexes:
        try:
            op.create_index('ix_users_id', 'users', ['id'], unique=False)
        except Exception:
            pass  # Index might already exist
    
    if 'ix_users_email' not in indexes:
        try:
            op.create_index('ix_users_email', 'users', ['email'], unique=True)
        except Exception:
            pass  # Index might already exist


def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')


Revision ID: 004
Revises: 003
Create Date: 2025-01-03

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
    # Check if table already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        # Create users table
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('email', sa.String(), nullable=False, unique=True),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )
    else:
        # Table exists - check and add missing columns
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'hashed_password' not in columns:
            op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
            # Update any existing rows with a placeholder (they'll need to reset password)
            op.execute("UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL")
            op.alter_column('users', 'hashed_password', nullable=False)
        
        if 'is_active' not in columns:
            op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
        
        if 'is_superuser' not in columns:
            op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
        
        if 'created_at' not in columns:
            op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        
        if 'updated_at' not in columns:
            op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Check if indexes exist before creating
    indexes = [idx['name'] for idx in inspector.get_indexes('users')] if 'users' in tables or 'users' not in tables else []
    
    if 'ix_users_id' not in indexes:
        try:
            op.create_index('ix_users_id', 'users', ['id'], unique=False)
        except Exception:
            pass  # Index might already exist
    
    if 'ix_users_email' not in indexes:
        try:
            op.create_index('ix_users_email', 'users', ['email'], unique=True)
        except Exception:
            pass  # Index might already exist


def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')

