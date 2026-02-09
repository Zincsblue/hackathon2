"""Add authentication tables

Revision ID: 002_add_authentication
Revises: 001_initial_schema
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_authentication'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend users table with authentication fields (email already exists from 001_initial_schema)
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))

    # Create unique constraint on email (if not already exists)
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # Create index on email for login lookups
    op.create_index('idx_users_email_lookup', 'users', ['email'])

    # Create index on is_active for filtering
    op.create_index('idx_users_is_active', 'users', ['is_active'])

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('replaced_by', sa.Integer(), nullable=True),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['replaced_by'], ['refresh_tokens.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('token_hash', name='uq_refresh_tokens_token_hash')
    )

    # Create indexes for refresh_tokens
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token_hash', name='uq_password_reset_tokens_token_hash')
    )

    # Create indexes for password_reset_tokens
    op.create_index('idx_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])
    op.create_index('idx_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])


def downgrade() -> None:
    # Drop password_reset_tokens table
    op.drop_index('idx_password_reset_tokens_user_id', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_token_hash', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

    # Drop refresh_tokens table
    op.drop_index('idx_refresh_tokens_expires_at', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    # Remove indexes from users table
    op.drop_index('idx_users_is_active', table_name='users')
    op.drop_index('idx_users_email_lookup', table_name='users')
    op.drop_constraint('uq_users_email', 'users', type_='unique')

    # Remove columns from users table (email stays - it was added in 001_initial_schema)
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'password_hash')
