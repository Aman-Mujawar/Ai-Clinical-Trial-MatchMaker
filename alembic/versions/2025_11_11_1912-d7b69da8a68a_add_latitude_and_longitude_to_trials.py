"""add latitude and longitude to trials

Revision ID: d7b69da8a68a
Revises: 64370c984b91
Create Date: 2025-11-11 19:12:17.204898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7b69da8a68a'
down_revision: Union[str, Sequence[str], None] = '64370c984b91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("trials", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("trials", sa.Column("longitude", sa.Float(), nullable=True))

def downgrade():
    op.drop_column("trials", "latitude")
    op.drop_column("trials", "longitude")