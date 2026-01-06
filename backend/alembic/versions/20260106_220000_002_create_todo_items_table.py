"""Create todo_items table

Revision ID: 002
Revises: 001
Create Date: 2026-01-06 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create todo_items table
    op.create_table(
        'todo_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(500), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for performance
    op.create_index('ix_todo_items_id', 'todo_items', ['id'], unique=False)
    op.create_index('ix_todo_items_user_id', 'todo_items', ['user_id'], unique=False)
    op.create_index('ix_todo_items_user_completed', 'todo_items', ['user_id', 'completed'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_todo_items_user_completed', table_name='todo_items')
    op.drop_index('ix_todo_items_user_id', table_name='todo_items')
    op.drop_index('ix_todo_items_id', table_name='todo_items')
    
    # Drop table
    op.drop_table('todo_items')
