"""add foreign keys for chatbot tables

Revision ID: 141da600c17e
Revises: cddfe2e391c4
Create Date: 2025-11-11 20:41:03.298144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '141da600c17e'
down_revision: Union[str, Sequence[str], None] = 'cddfe2e391c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_foreign_key(
        "fk_chatbot_messages_user", "chatbot_messages", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_chatbot_sessions_user", "chatbot_sessions", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

def downgrade():
    op.drop_constraint("fk_chatbot_messages_user", "chatbot_messages", type_="foreignkey")
    op.drop_constraint("fk_chatbot_sessions_user", "chatbot_sessions", type_="foreignkey")