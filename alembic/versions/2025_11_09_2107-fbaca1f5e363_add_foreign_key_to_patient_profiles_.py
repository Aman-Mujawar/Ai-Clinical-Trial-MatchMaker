"""Add foreign key to patient_profiles.user_id

Revision ID: fbaca1f5e363
Revises: e6b20a1f1727
Create Date: 2025-11-09 21:07:30.752011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbaca1f5e363'
down_revision: Union[str, Sequence[str], None] = 'e6b20a1f1727'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add foreign key to patient_profiles.user_id."""
    op.create_foreign_key(
        "fk_patient_profiles_user_id",
        "patient_profiles",        # source table
        "users",                   # referent table
        ["user_id"],               # local columns
        ["id"],                    # remote columns
        ondelete="CASCADE"         # optional, cascade delete
    )


def downgrade() -> None:
    """Downgrade schema: drop foreign key from patient_profiles.user_id."""
    op.drop_constraint(
        "fk_patient_profiles_user_id",
        "patient_profiles",
        type_="foreignkey"
    )
