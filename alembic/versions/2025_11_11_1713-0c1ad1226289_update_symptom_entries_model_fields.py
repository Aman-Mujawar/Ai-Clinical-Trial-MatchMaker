"""update symptom_entries model fields (safe version)

Revision ID: 0c1ad1226289
Revises: 6dc9746c0e7f
Create Date: 2025-11-11 17:13:43.404680
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '0c1ad1226289'
down_revision: Union[str, Sequence[str], None] = '6dc9746c0e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely — only add missing columns."""
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_columns = [col["name"] for col in inspector.get_columns("symptom_entries")]

    with op.batch_alter_table("symptom_entries", schema=None) as batch_op:
        # ✅ Add columns only if they don't already exist
        if "symptom_text" not in existing_columns:
            batch_op.add_column(sa.Column("symptom_text", sa.Text(), nullable=False))
        if "severity" not in existing_columns:
            batch_op.add_column(sa.Column("severity", sa.String(length=50), nullable=True))
        if "onset_date" not in existing_columns:
            batch_op.add_column(sa.Column("onset_date", sa.TIMESTAMP(timezone=True), nullable=True))

    # 🔒 No drop operations — we skip anything that doesn't exist


def downgrade() -> None:
    """Downgrade schema safely — only remove added columns."""
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_columns = [col["name"] for col in inspector.get_columns("symptom_entries")]

    with op.batch_alter_table("symptom_entries", schema=None) as batch_op:
        if "symptom_text" in existing_columns:
            batch_op.drop_column("symptom_text")
        if "severity" in existing_columns:
            batch_op.drop_column("severity")
        if "onset_date" in existing_columns:
            batch_op.drop_column("onset_date")
