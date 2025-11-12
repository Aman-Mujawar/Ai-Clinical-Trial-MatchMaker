"""update users table with new columns"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = 'a987a78832c7'
down_revision = '219d0cd766c0'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add new columns as nullable to avoid NOT NULL violation
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('address', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('medical_history', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('caregiver_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('caregiver_contact', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('specialization', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('license_number', sa.String(length=100), nullable=True))

    # Step 2: Optionally populate empty fields for existing users
    op.execute("UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL;")
    op.execute("UPDATE users SET last_name = 'Unknown' WHERE last_name IS NULL;")
    op.execute("UPDATE users SET phone_number = '' WHERE phone_number IS NULL;")
    op.execute("UPDATE users SET address = '' WHERE address IS NULL;")
    op.execute("UPDATE users SET gender = '' WHERE gender IS NULL;")
    op.execute("UPDATE users SET medical_history = '' WHERE medical_history IS NULL;")
    op.execute("UPDATE users SET caregiver_name = '' WHERE caregiver_name IS NULL;")
    op.execute("UPDATE users SET caregiver_contact = '' WHERE caregiver_contact IS NULL;")
    op.execute("UPDATE users SET specialization = '' WHERE specialization IS NULL;")
    op.execute("UPDATE users SET license_number = '' WHERE license_number IS NULL;")

    # Step 3 (Optional): make some columns non-nullable if needed later
    # Uncomment below lines only if you are sure no nulls remain in those columns
    # op.alter_column('users', 'first_name', nullable=False)
    # op.alter_column('users', 'last_name', nullable=False)


def downgrade():
    # Remove added columns in reverse order
    op.drop_column('users', 'license_number')
    op.drop_column('users', 'specialization')
    op.drop_column('users', 'caregiver_contact')
    op.drop_column('users', 'caregiver_name')
    op.drop_column('users', 'medical_history')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'address')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
