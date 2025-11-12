"""create chatbot_sessions table

Revision ID: cddfe2e391c4
Revises: 39a9128a96a8
Create Date: 2025-11-11 19:44:38.443192
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cddfe2e391c4'
down_revision: Union[str, Sequence[str], None] = '39a9128a96a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create chatbot_sessions table
    op.create_table(
        'chatbot_sessions',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('session_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('messages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_interaction', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('modified_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Make nct_id unique in trials table
    op.drop_index(op.f('ix_trials_nct_id'), table_name='trials')
    op.create_unique_constraint(None, 'trials', ['nct_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique constraint from trials
    op.drop_constraint(None, 'trials', type_='unique')
    op.create_index(op.f('ix_trials_nct_id'), 'trials', ['nct_id'], unique=True)

    # Drop chatbot_sessions table
    op.drop_table('chatbot_sessions')
