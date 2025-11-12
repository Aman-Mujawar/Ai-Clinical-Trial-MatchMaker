"""update users and patient_profiles tables

Revision ID: e6b20a1f1727
Revises: 30e0534e8f63
Create Date: 2025-11-09 20:59:25.963007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e6b20a1f1727'
down_revision = '30e0534e8f63'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema: drop prescreening column."""
    # Drop the 'prescreening' column from patient_profiles
    op.drop_column('patient_profiles', 'prescreening')


def downgrade() -> None:
    """Downgrade schema: restore prescreening column."""
    op.add_column(
        'patient_profiles',
        sa.Column(
            'prescreening',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default=sa.text("'{}'::jsonb")
        )
    )
