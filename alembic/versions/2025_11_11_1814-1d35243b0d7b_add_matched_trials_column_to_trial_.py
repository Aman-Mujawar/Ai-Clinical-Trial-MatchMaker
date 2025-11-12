"""Add matched_trials column to trial_matches

Revision ID: 1d35243b0d7b
Revises: 5e6e6f4ed46f
Create Date: 2025-11-11 18:14:13.618532
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # <--- add this

# revision identifiers, used by Alembic.
revision: str = '1d35243b0d7b'
down_revision: Union[str, Sequence[str], None] = '5e6e6f4ed46f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column(
        'trial_matches',
        sa.Column(
            'matched_trials',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default='[]'
        )
    )

def downgrade():
    op.drop_column('trial_matches', 'matched_trials')
