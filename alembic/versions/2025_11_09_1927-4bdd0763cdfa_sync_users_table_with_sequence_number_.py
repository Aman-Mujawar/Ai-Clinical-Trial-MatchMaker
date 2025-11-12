"""sync users table with sequence_number and new fields

Revision ID: 4bdd0763cdfa
Revises: a987a78832c7
Create Date: 2025-11-09 19:27:13.386819
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4bdd0763cdfa'
down_revision: Union[str, Sequence[str], None] = 'a987a78832c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Create sequence
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_seq START 1 INCREMENT 1;")

    # 2️⃣ Create ENUM type for status
    userstatus_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', name='userstatus', create_type=True)
    userstatus_enum.create(op.get_bind(), checkfirst=True)

    # 3️⃣ Add new columns
    op.add_column('users', sa.Column(
        'sequence_number', sa.Integer(), nullable=True, unique=True,
        server_default=sa.text("nextval('users_seq')")
    ))
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('status', userstatus_enum, nullable=True))
    op.add_column('users', sa.Column('profile_photo_url', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('terms_accepted', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_onboarded', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('modified_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')))

    # ✅ Fix for NOT NULL columns
    # Add as nullable first
    op.add_column('users', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('modified_by', postgresql.UUID(as_uuid=True), nullable=True))

    # Populate existing rows with dummy UUID
    op.execute("""
        UPDATE users
        SET created_by = '00000000-0000-0000-0000-000000000000',
            modified_by = '00000000-0000-0000-0000-000000000000'
        WHERE created_by IS NULL OR modified_by IS NULL;
    """)

    # Alter columns to NOT NULL
    op.alter_column('users', 'created_by', nullable=False)
    op.alter_column('users', 'modified_by', nullable=False)

    # Add is_deleted column
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')))

    # 4️⃣ Adjust existing columns
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(length=320), type_=sa.String(length=255), existing_nullable=False)
    op.alter_column('users', 'password_hash', existing_type=sa.TEXT(), type_=sa.String(length=255), existing_nullable=True)

    # 5️⃣ Indexes
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_is_verified'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'], unique=False)

    # 6️⃣ Drop old columns
    old_columns = [
        'date_of_birth', 'specialization', 'updated_at', 'deleted_at', 'consent_signed_at',
        'medical_history', 'accepted_tos_version', 'is_verified', 'gender', 'timezone',
        'is_active', 'license_number', 'address', 'mfa_enabled', 'accepted_privacy_version',
        'caregiver_contact', 'caregiver_name', 'locale', 'consent_research', 'name'
    ]
    for col in old_columns:
        op.drop_column('users', col)


def downgrade() -> None:
    # 1️⃣ Drop new columns
    new_columns = [
        'sequence_number', 'is_email_verified', 'status', 'profile_photo_url', 'bio',
        'location', 'terms_accepted', 'is_onboarded', 'modified_at', 'created_by',
        'modified_by', 'is_deleted'
    ]
    for col in new_columns:
        op.drop_column('users', col)

    # 2️⃣ Drop ENUM type
    userstatus_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', name='userstatus')
    userstatus_enum.drop(op.get_bind(), checkfirst=True)

    # 3️⃣ Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS users_seq;")
