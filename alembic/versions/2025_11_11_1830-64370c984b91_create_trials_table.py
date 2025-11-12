"""create trials table with seed data

Revision ID: 64370c984b91
Revises: 1d35243b0d7b
Create Date: 2025-11-11 18:30:33.822745
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid

# revision identifiers, used by Alembic.
revision: str = '64370c984b91'
down_revision: Union[str, Sequence[str], None] = '1d35243b0d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'trials',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('nct_id', sa.String(length=20), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('modified_at', sa.TIMESTAMP(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_trials_nct_id'), 'trials', ['nct_id'], unique=True)

    # Remove old constraints/columns if needed
    op.drop_constraint(op.f('patient_profiles_user_id_key'), 'patient_profiles', type_='unique')
    op.drop_constraint(op.f('patient_profiles_user_id_fkey'), 'patient_profiles', type_='foreignkey')
    op.drop_index(op.f('ix_symptom_entries_user_id'), table_name='symptom_entries')
    op.drop_column('trial_matches', 'results')

    # === Bulk insert seed data ===
    trials_table = table(
        'trials',
        column('id', postgresql.UUID),
        column('nct_id', sa.String),
        column('title', sa.Text),
        column('status', sa.String),
        column('location', sa.String),
        column('url', sa.Text),
        column('created_at', sa.TIMESTAMP),
        column('modified_at', sa.TIMESTAMP)
    )

    # Generate 50 dummy records
    trial_records = []
    statuses = ['Recruiting', 'Completed']
    locations = ['New York, USA', 'Boston, USA', 'Chicago, USA', 'Houston, USA', 'San Francisco, USA']
    titles = [
        'Cancer Immunotherapy', "Alzheimer's Study", 'Diabetes Trial', 'Heart Disease Research', 
        'Asthma Treatment', 'Depression Study', 'Obesity Intervention', 'Hypertension Study', 
        'Parkinson\'s Trial', 'COVID-19 Vaccine Study'
    ]

    now = datetime.utcnow()
    for i in range(1, 51):
        nct_id = f"NCT{100000+i}"
        title = titles[i % len(titles)] + f" Phase {i%4 + 1}"
        status = statuses[i % len(statuses)]
        location = locations[i % len(locations)]
        url = f"https://clinicaltrials.gov/{nct_id}"
        trial_records.append({
            'id': uuid.uuid4(),
            'nct_id': nct_id,
            'title': title,
            'status': status,
            'location': location,
            'url': url,
            'created_at': now,
            'modified_at': now
        })

    op.bulk_insert(trials_table, trial_records)


def downgrade() -> None:
    """Downgrade schema."""
    # Restore dropped columns/indexes/constraints
    op.add_column('trial_matches', sa.Column('results', sa.TEXT(), nullable=True))
    op.create_index(op.f('ix_symptom_entries_user_id'), 'symptom_entries', ['user_id'], unique=False)
    op.create_foreign_key(op.f('patient_profiles_user_id_fkey'), 'patient_profiles', 'users', ['user_id'], ['id'])
    op.create_unique_constraint(op.f('patient_profiles_user_id_key'), 'patient_profiles', ['user_id'], postgresql_nulls_not_distinct=False)

    op.drop_index(op.f('ix_trials_nct_id'), table_name='trials')
    op.drop_table('trials')
