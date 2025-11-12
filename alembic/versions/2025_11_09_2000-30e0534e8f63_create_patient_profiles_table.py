"""create patient_profiles table

Revision ID: 30e0534e8f63
Revises: 4bdd0763cdfa
Create Date: 2025-11-09 20:00:15.287539

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '30e0534e8f63'
down_revision: Union[str, Sequence[str], None] = '4bdd0763cdfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'patient_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'OTHER', 'UNKNOWN', name='genderenum'), nullable=True),
        sa.Column('blood_group', sa.Enum('A_POS', 'A_NEG', 'B_POS', 'B_NEG', 'AB_POS', 'AB_NEG', 'O_POS', 'O_NEG', 'UNKNOWN', name='bloodgroupenum'), nullable=True),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('diagnoses', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('allergies', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('medications', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('vaccinations', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('family_history', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('smoking_status', sa.Enum('NEVER', 'FORMER', 'CURRENT', 'UNKNOWN', name='smokingstatusenum'), nullable=True),
        sa.Column('alcohol_use', sa.String(length=64), nullable=True),
        sa.Column('occupation', sa.String(length=128), nullable=True),
        sa.Column('insurance', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('emergency_contact', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('prescreening', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('primary_provider_id', sa.UUID(), nullable=True),
        sa.Column('consent_to_share', sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column('contact_preference', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('modified_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('modified_by', sa.UUID(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_profiles_is_deleted'), 'patient_profiles', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_patient_profiles_user_id'), 'patient_profiles', ['user_id'], unique=True)
    op.drop_index(op.f('ix_users_is_deleted'), table_name='users')


def downgrade() -> None:
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'], unique=False)
    op.drop_index(op.f('ix_patient_profiles_user_id'), table_name='patient_profiles')
    op.drop_index(op.f('ix_patient_profiles_is_deleted'), table_name='patient_profiles')
    op.drop_table('patient_profiles')