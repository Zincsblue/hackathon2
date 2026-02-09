"""add conversations and messages tables

Revision ID: 003_add_chat_tables
Revises: 002_add_authentication
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_chat_tables'
down_revision = '002_add_authentication'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on conversations.user_id for efficient user-scoped queries
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role')
    )

    # Create indexes for messages table
    # Index on conversation_id for efficient history loading
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    # Index on created_at for chronological ordering
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])


def downgrade() -> None:
    # Drop messages table and its indexes
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table and its indexes
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
