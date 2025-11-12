"""make patient profile fields flexible

Revision ID: f0f9f6c0a150
Revises: 925d9a75547d
Create Date: 2025-11-10 13:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f0f9f6c0a150'
down_revision: Union[str, Sequence[str], None] = '925d9a75547d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: convert enums to strings safely."""
    # ### convert ENUM to STRING ###
    with op.batch_alter_table("patient_profiles") as batch_op:
        batch_op.alter_column(
            "gender",
            type_=sa.String(length=50),
            postgresql_using="gender::text",
            existing_nullable=True,
        )
        batch_op.alter_column(
            "blood_group",
            type_=sa.String(length=10),
            postgresql_using="blood_group::text",
            existing_nullable=True,
        )
        batch_op.alter_column(
            "smoking_status",
            type_=sa.String(length=50),
            postgresql_using="smoking_status::text",
            existing_nullable=True,
        )

    # ### drop old ENUM types safely ###
    op.execute("DROP TYPE IF EXISTS genderenum")
    op.execute("DROP TYPE IF EXISTS bloodgroupenum")
    op.execute("DROP TYPE IF EXISTS smokingstatusenum")

    # Note: Do NOT drop FK or UNIQUE unless required


def downgrade() -> None:
    """Downgrade schema: recreate ENUMs (may fail if free-text exists)."""
    # recreate ENUM types
    gender_enum = postgresql.ENUM('MALE', 'FEMALE', 'OTHER', 'UNKNOWN', name='genderenum')
    blood_enum = postgresql.ENUM('A_POS', 'A_NEG', 'B_POS', 'B_NEG', 'AB_POS', 'AB_NEG', 'O_POS', 'O_NEG', 'UNKNOWN', name='bloodgroupenum')
    smoking_enum = postgresql.ENUM('NEVER', 'FORMER', 'CURRENT', 'UNKNOWN', name='smokingstatusenum')

    gender_enum.create(op.get_bind(), checkfirst=True)
    blood_enum.create(op.get_bind(), checkfirst=True)
    smoking_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("patient_profiles") as batch_op:
        batch_op.alter_column(
            "gender",
            type_=gender_enum,
            postgresql_using="gender::genderenum",
            existing_nullable=True,
        )
        batch_op.alter_column(
            "blood_group",
            type_=blood_enum,
            postgresql_using="blood_group::bloodgroupenum",
            existing_nullable=True,
        )
        batch_op.alter_column(
            "smoking_status",
            type_=smoking_enum,
            postgresql_using="smoking_status::smokingstatusenum",
            existing_nullable=True,
        )
