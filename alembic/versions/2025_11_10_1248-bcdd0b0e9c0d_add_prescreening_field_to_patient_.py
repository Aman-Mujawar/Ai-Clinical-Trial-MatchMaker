"""add prescreening field to patient_profiles

Revision ID: bcdd0b0e9c0d
Revises: fbaca1f5e363
Create Date: 2025-11-10 12:48:07.793276

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '925d9a75547d'
down_revision: Union[str, Sequence[str], None] = 'fbaca1f5e363'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — add prescreening column."""
    op.add_column(
        'patient_profiles',
        sa.Column('prescreening', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema — drop prescreening column."""
    op.drop_column('patient_profiles', 'prescreening')