"""add symptom_entries table

Revision ID: 6dc9746c0e7f
Revises: f0f9f6c0a150
Create Date: 2025-11-11 17:02:49.574722
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6dc9746c0e7f'
down_revision: Union[str, Sequence[str], None] = 'f0f9f6c0a150'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new symptom_entries table
    op.create_table(
        'symptom_entries',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('symptom_text', sa.Text(), nullable=False),
        sa.Column('parsed_symptoms', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('onset_date', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('modified_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # Add index on user_id for faster queries
    op.create_index(op.f('ix_symptom_entries_user_id'), 'symptom_entries', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_symptom_entries_user_id'), table_name='symptom_entries')
    op.drop_table('symptom_entries')
